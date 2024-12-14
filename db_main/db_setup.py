from pymysql import connect, MySQLError
import re
import json
import pandas as pd
import random
import nltk
# from nltk.tokenize import word_tokenize
# from nltk import pos_tag
from nltk.corpus import wordnet
# from nltk.corpus import stopwords
# from nltk.stem import WordNetLemmatizer

# nltk.download('punkt')
nltk.download('wordnet')
# nltk.download('omw-1.4') 
# nltk.download('stopwords')

print("\n----------------------------CHATDB 95 – QUERYING HISTORICAL STOCK DATA----------------------------\n")

class ChatDB:
    def __init__(self, cred_json, db_index):
        """Initializes the ChatDB class and establishes a database connection."""
        self.conn = None
        self.query_patterns = {
            #"<A>": self._aggregate_by_query,
            "<A> by <B>": self._aggregate_by_query,
            "find <A> where <B> is <C>": self._find_where_query

        }


        try:
            # Load credentials from the JSON file
            with open(cred_json, 'r') as file:
                config = json.load(file)
                databases = config.get("db_cred", [])
                if not databases or db_index >= len(databases):
                    raise ValueError("Invalid database index or empty database configuration.")
            
            # Extract credentials
            db_info = databases[db_index]
            host = db_info.get("host")
            user = db_info.get("user")
            password = db_info.get("password")
            db_name = db_info.get("db_name")
            # db_name_display = db_info.get("name", "Unknown Database")

            self.conn = connect(
                host=host, 
                user=user, 
                password=password, 
                database=db_name
            )
            # print(f"Connected to {db_name_display} successfully")
            print(f"Connected to {db_name} successfully")
        except FileNotFoundError as e:
            print(f"The file '{cred_json}' was not found.")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from file '{cred_json}'.")
        except MySQLError as e:
            print(f"The error '{e}' occurred")
        except ValueError as e:
            print(f"Configuration error: {e}")
    
    def upload_dataset(self, file_path, table_name):
        """Uploads a CSV dataset to the specified table in the database."""
        if not self.conn:
            print("No active database connection.")
            return
        try:
            # Read the CSV file with pandas
            df = pd.read_csv(file_path)

            # Check if the table exists
            cursor = self.conn.cursor()
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            table_exists = cursor.fetchone()

            if table_exists:
                overwrite = input(f"Table '{table_name}' already exists. Overwrite? (y/n): ").lower()
                if overwrite != "y":
                    print("Upload canceled.")
                    return

            # Create a table structure based on the DataFrame
            columns = ", ".join([f"`{col}` TEXT" for col in df.columns])
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")

            # Insert data row by row
            for _, row in df.iterrows():
                values = "', '".join([str(value).replace("'", "''") for value in row])
                cursor.execute(f"INSERT INTO {table_name} VALUES ('{values}')")
            self.conn.commit()
            print(f"Dataset uploaded successfully to table '{table_name}'.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def close_connection(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

    def explore_database(self):
        """Lists tables and columns in the database and provides sample data."""
        if not self.conn:
            print("No active database connection.")
            return
        cursor = self.conn.cursor()
        
        # List the tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("\nTables in the database:")
        for idx, table in enumerate(tables, start=1):
            print(f"{idx} - {table[0]}")
        
        # Choose one of the tables
        try:
            table_choice = tables[int(input("\nYour choice of the table to explore: ")) - 1][0]
        except (IndexError, ValueError):
            print("Invalid choice. Please choose a valid table number.")
            return

        # List columns for the chosen table
        table_name = table_choice
        print(f"\nColumns in table '{table_name}':")
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        for column in columns:
            print(f" - {column[0]} ({column[1]})")
        
        # Fetch sample data
        print(f"\nSample data from '{table_name}':")
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
        rows = cursor.fetchall()
        
        # Use pandas to display the data
        if rows:
            column_names = [col[0] for col in columns]
            df = pd.DataFrame(rows, columns=column_names)
            print("\nSample Data:")
            print(df.to_markdown(index=False))
        else:
            print("No data found in the table.")


    def generate_query_examples(self, table_name, columns, construct=None):
        """Generates example SQL queries using templates with optional specific constructs."""

        queries = []
        # query_template = "SELECT <col> <function> FROM <table_name>"
        query_descriptions = []

        agg_func = [
            'SUM',
            'COUNT',
            'MAX',
            'MIN',
            'AVG'
        ]

        agg_keywords = {
            "SUM": ["sum", "total", "aggregate"],
            "AVG": ["average", "mean"],
            "MAX": ["max", "maximum", "greatest", "largest"],
            "MIN": ["min", "minimum", "least", "smallest"],
            "COUNT": ["count", "counting", "the number of"]
        }
        comparison_operators = {
            '=': 'equals',
            '>': 'greater than',
            '<': 'less than',
            '>=': 'greater than or equal to',
            '<=': 'less than or equal to',
            '!=': 'not equal to'
        }

        # Aggregation and GROUP BY examples using a pattern
        if len(columns) >= 2:
            if construct == '' or construct.lower() == 'aggregation':
                # Pattern: total (or other aggregate function) <A>
                func = random.choice(agg_func)
                column = random.choice(columns)
                queries.append(f"SELECT {func}({column}) FROM {table_name}")
                for i, value in agg_keywords.items():
                    if func == i:
                        query_descriptions.append(f"Find the {value[0]} of {column}")
                
        if len(columns) >= 2:
            if construct == '' or construct.lower() == 'group by':
                # Pattern: total (or other aggregate function) <A> by <B>
                func = random.choice(agg_func)
                agg_column = random.choice(columns)
                grouped_column = random.choice(columns)
                queries.append(f"SELECT {columns[0]}, {func}({agg_column}) FROM {table_name} GROUP BY {grouped_column}")
                for i, value in agg_keywords.items():
                    if func == i:
                        query_descriptions.append(f"Find the {value[0]} of {agg_column} by {grouped_column}")

        # ORDER BY example using a pattern
        if construct == '' or construct.lower() == 'order by':
            order_column = random.choice(columns)
            queries.append(f"SELECT * FROM {table_name} ORDER BY {order_column} DESC LIMIT 5")
            query_descriptions.append(f"Find all rows from {table_name} ordered by {order_column} in descending order with a limit of 5")
        
        # WHERE example with conditions using a pattern
        if construct == '' or construct.lower() == 'where':
            sample_value = 'some_value'
            where_column = random.choice(columns)
            operator = random.choice(list(comparison_operators.keys()))
            queries.append(f"SELECT * FROM {table_name} WHERE {where_column} {operator} '{sample_value}'")
            query_descriptions.append(f"Select all rows from {table_name} where {where_column} is {comparison_operators[operator]} '{sample_value}'")
        
        # Complex query example using a pattern
        if len(columns) >= 3 and (construct == '' or construct.lower() in ['group by', 'aggregation', 'where', 'order by']):
            sample_value = 'some_value'
            queries.append(f"SELECT {columns[0]}, {columns[1]}, {agg_func[0]}({columns[2]}) FROM {table_name} WHERE {columns[1]} = '{sample_value}' GROUP BY {columns[0]} ORDER BY {columns[2]} DESC")
            query_descriptions.append(f"Find {columns[0]}, {columns[1]}, and the total {columns[2]} using {agg_func[0]} from {table_name}, where {columns[1]} equals '{sample_value}', grouped by {columns[0]}, and ordered by {columns[2]} in descending order")
        
        # Shuffle the queries and descriptions together to keep them in sync
        combined = list(zip(query_descriptions, queries))
        random.shuffle(combined)
        query_descriptions, queries = zip(*combined) if combined else ([], [])

        return list(zip(query_descriptions, queries))

    def suggest_queries(self):
        """Suggests example queries for each table with optional constructs."""
        if not self.conn:
            print("No active database connection.")
            return            

        # List the tables
        cursor = self.conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        # Check if tables exist
        if not tables:
            print("No tables found in the database.")
            return
        
        print("\nTables in the database:")
        for idx, table in enumerate(tables, start=1):
            print(f"{idx} - {table[0]}")

        # Input validation loop
        while True:
            try:
                choice = int(input(f"\nYour choice of the table to explore (1 to {len(tables)}): "))
                
                if 1 <= choice <= len(tables):  # Validate range
                    table_name = tables[choice - 1][0]  # Extract table name
                    break
                else:
                    print(f"Invalid choice. Please enter a number between 1 and {len(tables)}.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")

        # Ask user if they want specific language constructs
        construct = input("\nEnter a specific language construct to use in the queries (e.g., 'group by', 'order by', 'where', 'aggregation'), or press Enter to skip: ").strip().lower()
        if construct not in ['', 'group by', 'order by', 'where', 'aggregation']:
            print("Invalid construct. Generating queries without specific construct.")
            construct = None

        # Proceed with the chosen table
        print(f"Selected table: {table_name}")
        cursor.execute(f"DESCRIBE {table_name}")
        columns = [col[0] for col in cursor.fetchall()]
        if columns:
            print(f"\nExample queries for table '{table_name}':")
            queries = self.generate_query_examples(table_name, columns, construct)
            if queries:
                for description, query in queries:
                    print(f" - {description}: \n{query}\n")
            else:
                print("No queries available for the selected construct.")

    def natural_language_to_sql(self, question, table_name, column_names):
        """
        Convert a natural language question into an SQL query for the given table.
        """
        # Preprocess and split the question
        cleaned_question = self._preprocess_question(question)
        # main_part, order_by_part = self._split_order_by(cleaned_question)

        # print(f"[DEBUG] Main Part: {main_part}")  # Debugging line
        # print(f"[DEBUG] Order By Part: {order_by_part}")  # Debugging line

        # Process the main query
        for pattern, function in self.query_patterns.items():
            if self._match_pattern(cleaned_question, pattern):  # Match main part with patterns
                try:
                    print(f"[DEBUG] Matched Pattern: {pattern}")  # Debugging line
                    sql_query = function(cleaned_question, table_name, column_names)

                    return sql_query
                except Exception as e:
                    print(f"[ERROR] Failed to process query for pattern '{pattern}'. Error: {e}")
                    return f"Error occurred while processing query with pattern '{pattern}': {str(e)}"

        print(f"[DEBUG] No matching pattern found for question: '{question}'")  # Debugging line
        return f"Query pattern not recognized for question: '{question}'"


    def _find_closest_column_name(self, term, column_names):
        from difflib import get_close_matches

        # Preprocess term and column names for matching
        term_normalized = term.lower().replace(' ', '_')
        column_names_normalized = [col.lower() for col in column_names]

        # Step 1: Exact match
        if term_normalized in column_names_normalized:
            match = column_names[column_names_normalized.index(term_normalized)]
            # print(f"[DEBUG] Exact match for '{term}': {match}")
            return match

        # Step 2: Check if any column contains the term as a substring
        substring_matches = [col for col in column_names if term_normalized in col.lower()]
        if substring_matches:
            # print(f"[DEBUG] Substring match for '{term}': {substring_matches[0]}")
            return substring_matches[0]  # Return the first substring match

        # Step 3: Fuzzy matching (fallback)
        matches = get_close_matches(term_normalized, column_names_normalized, n=1, cutoff=0.5)
        if matches:
            match = column_names[column_names_normalized.index(matches[0])]
            # print(f"[DEBUG] Fuzzy match for '{term}': {match}")
            return match

        # Step 4: No match, return normalized term
        # print(f"[DEBUG] No close match found for '{term}', using raw term.")
        return term_normalized

    def _preprocess_question(self, question):
        phrase_replacements = {
            "by": ["broken down by"],
            "total": ["total", "sum", "aggregate"],
            "average": ["average", "mean", "avg"],
            "count": ["count", "the number of", "how many"]
        }
        question = question.lower()
        for replacement, phrases in phrase_replacements.items():
            for phrase in phrases:
                if f" {phrase} " in f" {question} ": 
                    question = question.replace(phrase, replacement)
        question = re.sub(r'\s+', ' ', question).strip()
        return question


    def _match_pattern(self, question, pattern):
        """
        Match the question against a pattern with placeholders 
        (e.g., <A>, <B>, <C>) replaced by regex groups.
        """
        try:
            # Debug: Print original pattern
            # print(f"[DEBUG] Original Pattern: {pattern}")
            # Replace placeholders (e.g., <A>, <B>, <C>) with regex groups
            regex = re.sub(r"<\w+>", r"([a-zA-Z0-9_ ]+)", pattern)
            
            # Debug: Print the compiled regex
            # print(f"[DEBUG] Compiled Regex: {regex}")
            
            # Check if the regex matches the question
            match = re.search(regex, question)
            # print(f"[DEBUG] Regex Match: {match is not None}")  # Debug match result
            return match is not None
        except re.error as e:
            # print(f"[ERROR] Invalid regex pattern: {pattern}. Error: {e}")
            return False
        
    # def _split_order_by(self, question):
    #     # Split the question into main and ORDER BY parts
    #     if "order by" in question.lower():
    #         main_part, order_by_part = question.lower().split("order by", 1)
    #         return main_part.strip(), order_by_part.strip()
    #     return question.strip(), None

    def _aggregate_by_query(self, question, table_name, column_names):
        """
        Generate an SQL query for aggregation functions (SUM, AVG, COUNT) with GROUP BY.
        """
        # Define supported aggregation functions and their keywords
        aggregation_functions = {
            "sum": "SUM",
            "total": "SUM",
            "avg": "AVG",
            "average": "AVG",
            "mean": "AVG",
            "count": "COUNT",
            "the number of": "COUNT",
            "max": "MAX",
            "maximum": "MAX",
            "greatest": "MAX",
            "largest": "MAX",
            "top": "MAX",
            "min": "MIN",
            "minimum": "MIN",
            "least": "MIN",
            "bottom": "MIN"
        }
        
        # Detect the aggregation function and match the query pattern
        for keyword, func in aggregation_functions.items():
            
            # Regex to match "total <A> by <B>" or similar patterns
            match1 = re.search(fr"{keyword} ([\w\s]+) by ([\w\s]+)", question)
            match2 = re.search(fr"{keyword} ([\w\s]+)", question)
            #match3 = re.search(fr"([\w\s]+)", question)
            if match1:
                # Extract column names from the matched groups
                column_a = self._find_closest_column_name(match1.group(1).strip(), column_names)
                column_b = self._find_closest_column_name(match1.group(2).strip(), column_names)
                # Return the SQL query
                return f"SELECT {column_b}, {func}({column_a}) FROM {table_name} GROUP BY {column_b};"
            elif match2: # Aggregate only with no Group By Clause
                # Extract column names from the matched groups
                column_a = self._find_closest_column_name(match2.group(1).strip(), column_names)
                # Return the SQL query
                return f"SELECT {func}({column_a}) FROM {table_name};"
            # elif match3: 
            #     # Extract column names from the matched groups
            #     column_a = self._find_closest_column_name(match3.group(1).strip(), column_names)
            #     # Return the SQL query
            #     return f"SELECT {column_a} FROM {table_name};"
            
        return "Invalid query format."


    def _find_where_query(self, question, table_name, column_names):
        match = re.search(r"find ([\w\s]+) where ([\w\s]+) is ([\w\s]+)", question)
        if match:
            a = self._find_closest_column_name(match.group(1).strip(), column_names)
            b = self._find_closest_column_name(match.group(2).strip(), column_names)
            c = match.group(3).strip()  # No need to validate values
            return f"SELECT {a} FROM {table_name} WHERE {b} = '{c}';"
        return "Invalid query format."

    def _append_order_by(self, sql_query, order_by_part, column_names):
        """
        Append an ORDER BY clause to an existing SQL query.
        """
        # Regex to detect the column and order (ascending/descending)
        match = re.search(r"([\w\s]+)(?: (ascending|descending))?", order_by_part)
        if match:
            column = self._find_closest_column_name(match.group(1).strip(), column_names)
            order = match.group(2) or "ascending"  # Default to ascending if not specified
            order_sql = "ASC" if order.lower() == "ascending" else "DESC"

            # Append the ORDER BY clause
            if ";" in sql_query:  # Remove the semicolon if it exists
                sql_query = sql_query.rstrip(";")
            return f"{sql_query} ORDER BY {column} {order_sql};"

        # print(f"[DEBUG] Invalid ORDER BY part: {order_by_part}")  # Debugging line
        return sql_query

    def execute_query(self):
        """Executes a SQL query and returns the results."""
        if not self.conn:
            print("No active database connection.")
            return
        cursor = self.conn.cursor()

        # List the tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("\nTables in the database:")
        for idx, table in enumerate(tables, start=1):
            print(f"{idx} - {table[0]}")
        
        query = input("Enter your SQL query: ")

        try:
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(results, columns=columns)
            print("\nQuery Results:")
            print(df.to_markdown(index=False))
        except MySQLError as e:
            print(f"The error '{e}' occurred")



