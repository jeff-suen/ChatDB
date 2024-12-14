from db_setup import ChatDB 

def main():
    """Main function for the ChatDB CLI."""
    print("Choose a database to connect to:")
    print("1: stock_mag7")
    print("2: etf_indexes")
    print("3: etf_biotech_top3")
    
    db_index = int(input("Enter the index of the database (1-3): ")) - 1
    chatdb = ChatDB("db_cred.json", db_index)
    print("\n-----------------------------------------------------------------------------------------\n")
    print("Welcome to ChatDB! - QUERYING HISTORICAL STOCK DATA")
    while True:
        print("\nChoose an option:")
        print("1. Explore tables in the database")
        print("2. Suggest example queries with or with no specified langauage constructs")
        print("3. Convert natural language to SQL")
        print("4. Execute a query")
        print("5. Upload a dataset")
        print("6. Exit")

        choice = input("\nYour choice: ")
        if choice == "1":
            chatdb.explore_database()
        elif choice == "2":
            chatdb.suggest_queries()
        elif choice == "3":
            # List the tables
            cursor = chatdb.conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            print("\nTables in the database:")
            for idx, table in enumerate(tables, start=1):
                print(f"{idx} - {table[0]}")

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

            cursor.execute(f"DESCRIBE {table_name}")
            columns = [col[0] for col in cursor.fetchall()]

            print(f"\nColumns in `{table_name}`: {', '.join(columns)}")
            nl_query = input("Enter your natural language query: ")
            sql_query = chatdb.natural_language_to_sql(nl_query, table_name, columns)
            print(f"Generated SQL: {sql_query}")

        elif choice == "4":
            chatdb.execute_query()

        elif choice == "5":
            file_path = input("Enter the CSV file path: ")
            table_name = input("Enter the table name to store the dataset: ")
            chatdb.upload_dataset(file_path, table_name)

        elif choice == "6":
            print("Goodbye!")
            chatdb.close_connection()
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

