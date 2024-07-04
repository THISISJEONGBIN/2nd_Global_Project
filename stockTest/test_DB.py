from unittest import result
import pytest
import unittest
import pymysql as db
import logging
logger = logging.getLogger(__name__)


@pytest.fixture(scope='module',autouse=True)
def connection_db():
    connection = db.connect(host='127.0.0.1', user='root', password='1234', db='stock', charset='utf8')
    yield
    connection.close()

class TestDataset(unittest.TestCase):
    test_data =[
        ('abc','1234','aaa','bbb'),
        ('bcd', '1124', 'fda', 'bfbb'),
        ('atee', '1986', 'ada', 'bbrsb')
    ]

    def get_test_data(self):
        connection = db.connect(host='127.0.0.1', user='root', password='1234', db='stock', charset='utf8')
        cur = connection.cursor()
        cur.execute("select * from usertb")
        result = cur.fetchall()
        return result

    def test_de(self):
        self.assertEqual(result,TestDataset.test_data)



