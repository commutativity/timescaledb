import unittest
from home import ticker_comparison, get_data, get_companies, update_database


class TestHome(unittest.TestCase):
    """
    Test the functions in Home.py
    """
    def test_ticker_comparison(self):
        database_symbols = get_data()
        file_path = '..//src//data//us_market_cap.csv'
        top_symbols = get_companies(file_path, limit=102)
        top_tickers_prep = ticker_comparison(database_symbols, top_symbols)
        self.assertEqual(len(top_tickers_prep), 100)
        self.assertEqual(top_tickers_prep[0], 'AAPL')
        self.assertEqual(top_tickers_prep[99], 'NOC')
        # print(top_tickers_prep)

    def test_update_database(self):
        tickers = ('AAPL', 'TWTR')
        update_database(tickers)

    def test_get_companies(self):
        file_path = '..//src//data//us_market_cap.csv'
        data = get_companies(file_path, limit=2)
        self.assertEqual(data, ['AAPL', 'MSFT'])
        # print(data)