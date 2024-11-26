# CHATDB – QUERYING HISTORICAL STOCK DATA

ChatDB is a Python-based Command Line Interface (CLI) tool designed for querying and managing MySQL databases. It provides seamless interaction with databases, offering features such as natural language-to-SQL conversion, dataset uploads, query execution, and table exploration. The primary focus of ChatDB is to create an interactive application that enables users to access historical financial data, including information like open prices, close prices, highs, lows, trading volume, and more. Users can interact with the CLI using sample query languages to retrieve and explore historical financial insights efficiently.


---

## Features

- **Database Connectivity**: Connect to MySQL databases using credentials stored in a JSON file.
- **Explore Tables**: List all tables in the database and view their columns and sample data in a tabular format.
- **Query Suggestions**: Generate SQL queries with constructs like `GROUP BY`, `ORDER BY`, and `WHERE`.
- **Natural Language to SQL**: Convert plain English queries into SQL statements.
- **Upload Datasets**: Upload CSV files into database tables with ease.
- **Execute SQL Queries**: Run custom SQL queries and view results in a formatted table.
- **Interactive CLI**: User-friendly menu interface for seamless interaction.

---

## Prerequisites

Before running the tool, ensure you have the following:

1. **Python 3.7 or higher**
2. **MySQL Server** installed and running
3. Required Python libraries:
   - `pymysql`
   - `pandas`
   - `tabulate`

Install dependencies using:
```bash
pip install pymysql pandas tabulate
