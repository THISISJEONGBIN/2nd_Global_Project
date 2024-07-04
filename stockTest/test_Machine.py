import unittest
import pandas as pd
import pjMachine as pjMachine
import parameterized
from sklearn.metrics import r2_score

import logging
logger = logging.getLogger(__name__)


class MachineLearnTest(unittest.TestCase):
    csv_stock = 'C:\\Users\\yiseul\\DataspellProjects\\Pj_stock\\test\\StockCode.csv'
    #csv_stock = 'C:\\Users\\A002\\Documents\\Code\\pyPython\\project\\test\\StockCode.csv'
    df = pd.read_csv(csv_stock, nrows=200)
    @parameterized.parameterized.expand([(row.iloc[0]) for _, row in df.iterrows()])
    def test_MachineLearn_valid(self, copId) :
            X_train, X_test, y_train, y_test, y_pred, closeStock, realStock, futureFrame10, futureFrame30, stockData30, todayClose, tomorrow_pred, realStock, r2, stockData = pjMachine.learnData(copId)

            # 예측 성능 평가
            r2_score_value = r2_score(y_test, y_pred)
            print(r2_score_value)
            if r2_score_value < 0.8:
                self.fail(f"R^2 score {r2_score_value} is less than 0.8")

            # 예측 성능이 기준(예: 0.8 이상)을 충족하는지 검증
            self.assertGreaterEqual(r2_score_value, 0.8)

            # 결과가 None이 아닌지 확인
            self.assertIsNotNone(X_train)
            self.assertIsNotNone(X_test)
            self.assertIsNotNone(y_train)
            self.assertIsNotNone(y_test)
            self.assertIsNotNone(y_pred)
            self.assertIsNotNone(closeStock)
            self.assertIsNotNone(realStock)
            self.assertIsNotNone(futureFrame10)
            self.assertIsNotNone(futureFrame30)
            self.assertIsNotNone(stockData30)
            self.assertIsNotNone(todayClose)
            self.assertIsNotNone(tomorrow_pred)
            self.assertIsNotNone(realStock)
            self.assertIsNotNone(r2)
    if __name__ == '__main__':
        unittest.main()