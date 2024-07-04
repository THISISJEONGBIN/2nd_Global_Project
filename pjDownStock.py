import FinanceDataReader as fdr
import pjMydb as pjMydb

# fdr을 이용하여 데이터 다운로드 후 DB 저장 및 return
def downloadStock(tracker, startDate, startDate30, endDate) :
    stockData = fdr.DataReader(tracker, startDate, endDate)
    if stockData.empty :
        return None
    else :
        stockData.sort_index(inplace=True)
        stockDB = pjMydb.saveStock(tracker, stockData)
        stockData30 = fdr.DataReader(tracker, startDate30, endDate)
        return stockDB, stockData30

# DB에 저장된 데이터 중 종가에 대한 지도학습을 하기위해 학습 데이터 생성
# 추가로 realStock은 현재 종가에 대한 값을 저장
def findCloseStock(stockData) :
    closeStock = stockData[['SK_CLOSE']].copy()
    for i in closeStock[['SK_CLOSE']].tail().iloc :
        realStock = i.values[0]
    closeStock['NextClose'] = closeStock[['SK_CLOSE']].shift(-1)
    closeStock = closeStock.iloc[:-1]
    return closeStock, realStock

