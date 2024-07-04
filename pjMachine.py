import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from datetime import datetime, timedelta
import pjDownStock

# Scrap을 해온 주식 코드를 이용하여 지도학습 해주는 코드
def learnData(stockTarget) :
    target = str(stockTarget) # 주식 코드
    startDate = (datetime.today() - timedelta(days=5*365)).strftime('%Y-%m-%d') # 5년치의 날짜 데이터
    startDate30 = (datetime.today() - timedelta(days=50)).strftime('%Y-%m-%d') # 50일치의 날짜 데이터
    endDate = datetime.today().strftime('%Y-%m-%d') # 오늘 날짜
    stockData, stockData30 = pjDownStock.downloadStock(target, startDate, startDate30, endDate) # fdr을 이용한 데이터 5년치와 50일치의 데이터 반환
    if stockData.empty :
        return None

    closeStock, realStock = pjDownStock.findCloseStock(stockData) # close(종가)데이터 중 실제데이터 + 학습데이터, 어제 실제 종가 반환
    closeStock = pd.DataFrame(closeStock) # 지도학습을 위한 데이터 프레임화

    X = closeStock[['SK_CLOSE']]  # 종가 실제데이터
    y = closeStock['NextClose'] # 종가 학습데이터
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.8, shuffle=False)
    linearModel = LinearRegression()
    linearModel.fit(X_train, y_train)
    y_pred = linearModel.predict(X_test)

    todayClose = pd.DataFrame(closeStock.iloc[-1][['SK_CLOSE']].values.reshape(-1,1), columns = ['SK_CLOSE']) # 오늘날의 종가 데이터 df화
    tomorrow_pred = linearModel.predict(todayClose) # 오늘날의 종가 데이터를 가지고 내일의 종가데이터 예측
    r2 = r2_score(y_test, y_pred) # 정확도 확인

    future_pred30 = [] # 30일의 예측데이터를 저장하기 위한 리스트
    future_pred10 = [] # 10일의 예측데이터를 저장하기 위한 리스트
    currentPrice = todayClose.values.reshape(-1,1) # 오늘날의 종가 데이터 2차원 배열 형태로 변형

    for _ in range(30) : # 30일 이후의 종가데이터를 예측하기 위한 반복문
        nextPrice = linearModel.predict(currentPrice) # 오늘날의 종가 데이터를 가지고 내일의 종가데이터 예측
        future_pred30.append(nextPrice[0]) # # nextPrice가 2차원 배열이므로 리스트에 저장하기 위해 0번째 데이터를 pred30에 1차원 배열 형태로 저장
        currentPrice = nextPrice.reshape(-1,1) # 다음날을 예측하기 위해 currentPrice를 다시 2차원 배열 형태로 변형

    futureDate30 = pd.date_range(start=datetime.today().strftime('%Y-%m-%d'), periods=30, freq='B') # 30일 이후의 날짜를 배열 형태로 저장
    futureFrame30 = pd.DataFrame(future_pred30, index=futureDate30, columns=['PredClose']) # 30일 이후 날짜 데이터와 예측데이터를 df화

    for _ in range(11) : # 위와 동일함
        nextPrice = linearModel.predict(currentPrice)
        future_pred10.append(nextPrice[0])
        currentPrice = nextPrice.reshape(-1,1)

    futureDate10 = pd.date_range(start=datetime.today().strftime('%Y-%m-%d'), periods=11, freq='B')
    futureFrame10 = pd.DataFrame(future_pred10, index=futureDate10, columns=['PredClose'])
    futureFrame10['Multi'] = futureFrame10['PredClose'].diff() # 전일비를 구하기 위한 df의 열 생성
    futureFrame10 = futureFrame10.dropna() # NAN데이터 drop

    return X_train, X_test, y_train, y_test, y_pred, closeStock, realStock, futureFrame10, futureFrame30, stockData30, todayClose, tomorrow_pred, realStock, r2, stockData