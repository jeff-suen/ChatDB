# ChatDB - Querying Historical Stock Data

## Overview
ChatDB is a command-line application designed to query historical stock data using both SQL queries and natural language inputs. Users can upload datasets, explore databases, generate SQL queries from natural language, and execute SQL queries on the connected database.

---

## File Structure

### **1. `db_main/`**
This directory contains the core application code for ChatDB.

- **`db_setup.py`**:
  - Defines the `ChatDB` class, which handles database connection, query generation, and execution.
  - Includes functions for natural language processing, SQL query generation, and dataset upload.

- **`db_cred.json`**:
A JSON file containing database credentials. The structure is as follows:
```json
{
  "db_cred": [
    {
      "host": "<DB_HOST>",
      "user": "<DB_USER>",
      "password": "<DB_PASSWORD>",
      "db_name": "<DB_NAME>"
    }
  ]
}
```
**Note**: Replace placeholders (`<DB_HOST>`, `<DB_USER>`, etc.) with actual database connection details.

- **`main.py`**:
The entry point for the application. Handles user interaction through the command-line interface and provides the following features:
- Database exploration
- Query suggestion
- Natural language to SQL conversion
- Query execution
- Dataset upload

### **2. `data/`**
Directory to store CSV datasets for upload to there databases.

---

## Prerequisites

1. **Python**: Ensure Python 3.x is installed on your system.
2. **Dependencies**:
   Install required Python packages:
   ```bash
   pip install pymysql pandas nltk
   ```
3. **Database**:
   Set up the database and populate `db_cred.json` with connection details.
4. **NLTK Resources**:
   Download necessary NLTK data:
   ```bash
   python -c "import nltk; nltk.download('wordnet')"
   ```

---

## Commands to Run the Program

1. **Navigate to the Project Directory**:
   ```bash
   cd final_proj
   ```

2. **Run the Application**:
   ```bash
   python main.py
   ```

---

## Features and How to Use Them

1. **Explore Tables in the Database**:
   - Select option `1` to list tables and their columns, along with sample data.

2. **Suggest Example Queries**:
   - Select option `2` to generate SQL query examples for the selected table. You can optionally specify constructs like `GROUP BY`, `WHERE`, etc.

3. **Convert Natural Language to SQL**:
   - Select option `3`.
   - Choose a table from the database.
   - Enter a natural language query (e.g., `total sales by category`).
   - The program will generate and display an equivalent SQL query.

4. **Execute a SQL Query**:
   - Select option `4`.
   - Enter a valid SQL query to execute on the database.
   - Results will be displayed in a tabular format.

5. **Upload a Dataset**:
   - Select option `5`.
   - Provide the path to a CSV file and specify the table name for storage in the database.

6. **Exit the Program**:
   - Select option `6` to close the database connection and exit the program.

---

## Example Workflow

1. Start the program:
   ```bash
   python main.py
   ```
2. Connect to a database by selecting its index.
3. Explore tables or upload a dataset as needed.
4. Enter natural language queries like:
   - `total revenue by product`
   - `average price where category is electronics`
5. Execute SQL queries directly for advanced operations.

---

## Notes
- Ensure the database connection details in `db_cred.json` are correct.
- Uploaded datasets should be in CSV format and match the database schema for seamless integration.

---

For further questions or issues, feel free to contact the developer.

