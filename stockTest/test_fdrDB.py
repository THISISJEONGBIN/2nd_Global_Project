import unittest
import pjDownStock
import pandas as pd
import parameterized
from datetime import timedelta, datetime
import pymysql as db

import logging
logger = logging.getLogger(__name__)



class TestFdrDB(unittest.TestCase):
    csv_stock = 'C:\\Users\\yiseul\\DataspellProjects\\Pj_stock\\test\\StockCode.csv'
    #csv_stock = 'C:\\Users\\A002\\Documents\\Code\\pyPython\\project\\test\\StockCode.csv'
    df = pd.read_csv(csv_stock, nrows=200)
    @parameterized.parameterized.expand([(row.iloc[0]) for _, row in df.iterrows()])
    def test_fdrDB_valid(self, copId) :
        target = str(copId)
        startDate = (datetime.today() - timedelta(days=5*365)).strftime('%Y-%m-%d')
        startDate30 = (datetime.today() - timedelta(days=50)).strftime('%Y-%m-%d')
        endDate = datetime.today().strftime('%Y-%m-%d')
        testData, testData30 = pjDownStock.downloadStock(target, startDate, startDate30, endDate)
        try :
            stockCode = "st"+copId
            conn = db.connect(host='127.0.0.1', user='root', password='1234', db='stock', charset='utf8')
            cur = conn.cursor()
            cur.execute("SELECT table_name FROM INFORMATION_SCHEMA.TABLES WHERE table_schema = 'stock' AND table_name LIKE 'ST%'")
            table_list = [row[0] for row in cur.fetchall()]
            for j, i in enumerate(table_list) :
                if i == stockCode :
                    table_list.sort()
                    table_to_drop = table_list[j]
                    cur.execute(f"DROP TABLE {table_to_drop}")
                    print(f"testData dropTable {table_to_drop}")
            cur.close()
            conn.close()
        except db.DatabaseError :
            pass
        if testData.empty :
            self.fail('Empty DataFrame')
        else :
            self.assertIsNotNone(testData)
            self.assertIsNotNone(testData30)

    @parameterized.parameterized.expand([('aaaaa'), ('jdfkasdjf'),('가나다'), ('박이슬'), ('한석희'), ('김정빈'), ('장으뜸'), ('글로벌')])
    def test_fdrDB_invalid(self, copId) :
        target = str(copId)
        startDate = (datetime.today() - timedelta(days=5*365)).strftime('%Y-%m-%d')
        startDate30 = (datetime.today() - timedelta(days=50)).strftime('%Y-%m-%d')
        endDate = datetime.today().strftime('%Y-%m-%d')
        testData, testData30 = pjDownStock.downloadStock(target, startDate, startDate30, endDate)
        if testData.empty :
            self.fail('Empty DataFrame')
        else :
            self.assertIsNotNone(testData)
            self.assertIsNotNone(testData30)
