import unittest
from db_main.db_setup import ChatDB 

class TestChatDB(unittest.TestCase):
    def setUp(self):
        """Set up test cases and ChatDB instance."""
        self.chatdb = ChatDB("test_cred.json", 0)  # Mocked credentials
        self.table_name = "aapl"
        self.columns = ["Date", "Open", "High", "Low", "Adj Close", "Volume"]

    def test_aggregation(self):
        """Test aggregation in NLQ to SQL conversion."""
        nl_query = "Find the total open price grouped by date"
        expected_sql = "SELECT SUM(open) FROM aapl GROUP BY date"
        generated_sql = self.chatdb.nl_to_sql(nl_query, self.table_name, self.columns)
        self.assertEqual(generated_sql.strip(), expected_sql.strip())

    def test_ordering(self):
        """Test ordering in NLQ to SQL conversion."""
        nl_query = "Sort data by region ascending"
        expected_sql = "SELECT * FROM aapl ORDER BY volume ASC"
        generated_sql = self.chatdb.nl_to_sql(nl_query, self.table_name, self.columns)
        self.assertEqual(generated_sql.strip(), expected_sql.strip())

    def test_filtering(self):
        """Test filtering in NLQ to SQL conversion."""
        nl_query = "Show data where date = '2021-01-01'"
        expected_sql = "SELECT * FROM aapl WHERE date = '2021-01-01'"
        generated_sql = self.chatdb.nl_to_sql(nl_query, self.table_name, self.columns)
        self.assertEqual(generated_sql.strip(), expected_sql.strip())

    def test_full_query(self):
        """Test full query conversion."""
        nl_query = "Find total open grouped by date sorted by volume descending"
        expected_sql = (
            "SELECT date, SUM(open) FROM aapl "
            "GROUP BY date ORDER BY volume DESC"
        )
        generated_sql = self.chatdb.nl_to_sql(nl_query, self.table_name, self.columns)
        self.assertEqual(generated_sql.strip(), expected_sql.strip())

if __name__ == "__main__":
    unittest.main()
