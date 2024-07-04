from lib2to3.pgen2 import driver
from pjScrap import findCopId
import unittest
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from parameterized import parameterized
import pandas as pd

import logging
logger = logging.getLogger(__name__)

#read = pd.read_excel('C:\\Users\\A002\\Documents\\Code\\pyPython\\project\\test\\corp.xlsx', usecols='A', skiprows=1, nrows=201)
read = pd.read_excel('C:\\Users\\yiseul\\DataspellProjects\\Pj_stock\\test\\corp.xlsx', usecols='A', skiprows=1, nrows=201)
class TestFindCopId(unittest.TestCase):
    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)

    @parameterized.expand([(read.iloc[i, 0],) for i in range(len(read))])
    def test_findCopId_valid(self, data):
        copId = findCopId(data)
        if copId is False:
            self.fail()
        else : self.assertIsNotNone(copId)

    def tearDown(self):
        try:
            self.driver.close()
        except AttributeError:
            pass

if __name__ == "__main__":
    unittest.main()
