import unittest
import pjDownStock
import FinanceDataReader as fdr
import pandas as pd
import parameterized
from datetime import timedelta, datetime
import pymysql as db
import logging
import os


logger = logging.getLogger(__name__)
#info test 시작 기록

class closeDB(unittest.TestCase):
    csv_stock = 'C:\\Users\\yiseul\\DataspellProjects\\Pj_stock\\test\\StockCode.csv'
    #csv_stock = 'C:\\Users\\A002\\Documents\\Code\\pyPython\\project\\test\\StockCode.csv'
    df = pd.read_csv(csv_stock, nrows=200)
    @parameterized.parameterized.expand([(row.iloc[0]) for _, row in df.iterrows()])
    def test_closeDB_valid(self, copId) :
        startDate = (datetime.today() - timedelta(days=5*365)).strftime('%Y-%m-%d')
        endDate = datetime.today().strftime('%Y-%m-%d')
        try:
            stockData = fdr.DataReader(copId, startDate, endDate)
            stockDf = stockData[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            stockDf.columns = ['SK_OPEN', 'SK_HIGH', 'SK_LOW', 'SK_CLOSE', 'SK_VOLUME']
            closeStock, realStock = pjDownStock.findCloseStock(stockDf)
            if realStock :
                self.assertIsNotNone(closeStock)
                self.assertIsNotNone(realStock)
            else :
                logger.error(f'Failed test for copId: {copId} - None Data')
                self.fail("None Data")
        except Exception as e:
            logger.exception(f'Exception occurred for copId: {copId}')
            self.fail(f'Exception occurred: {e}')


    @parameterized.parameterized.expand([('dasdsa'), ('2fwqewq'),('qwe123'), ('qazxwds'), ('dsadasd'), ('qqqqqqqq'), ('2wwwww'), ('eeeeeee')])
    def test_closeDB_invalid(self, copId) :
        startDate = (datetime.today() - timedelta(days=5*365)).strftime('%Y-%m-%d')
        endDate = datetime.today().strftime('%Y-%m-%d')
        try:
            stockData = fdr.DataReader(copId, startDate, endDate)
            stockDf = stockData[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            stockDf.columns = ['SK_OPEN', 'SK_HIGH', 'SK_LOW', 'SK_CLOSE', 'SK_VOLUME']
            closeStock, realStock = pjDownStock.findCloseStock(stockDf)
            if realStock :
                self.assertIsNotNone(closeStock)
                self.assertIsNotNone(realStock)
            else :
                logger.info(f'Correctly identified invalid copId: {copId}') #error 로그 기록
                self.fail("None Data")
        except Exception as e:
            logger.exception(f'Exception occurred for copId: {copId}') #예외처리
            self.fail(f'Exception occurred: {e}')