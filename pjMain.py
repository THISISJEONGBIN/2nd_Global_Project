from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from selenium import webdriver
from selenium.webdriver.common.by import By
import matplotlib.pyplot as plt
import mplfinance as mpf
from matplotlib.backends.backend_qt5agg import FigureCanvas as FigureCanvas
import webbrowser as wb
import pandas as pd
import time
import pjMachine
import pjScrap
from tkinter import messagebox
import FinanceDataReader as fdr
import logging
import sys
import os

if hasattr(sys, '_MEIPASS') :
    base_path = sys._MEIPASS
else :
    base_path = os.path.abspath(".")

login_path = os.path.join(base_path, 'resources', 'images', 'Loginpage_logo.png')
eur_path = os.path.join(base_path, 'resources', 'images', 'EUR.png')
jpn_path = os.path.join(base_path, 'resources', 'images', 'JPN.png')
kor_path = os.path.join(base_path, 'resources', 'images', 'KOR.png')
usa_path = os.path.join(base_path, 'resources', 'images', 'USA.png')


logging.getLogger('matplotlib').setLevel(logging.INFO)

options = webdriver.ChromeOptions()
options.add_argument("headless")
driver = webdriver.Chrome(options=options)
driver.get('https://finance.daum.net/news#economy')
driver.implicitly_wait(50)
driver2 = webdriver.Chrome(options=options)
driver2.get('https://finance.daum.net/')
driver2.implicitly_wait(50)

news_link = []
news_title = []

news_title.append(driver.find_element(by=By.CLASS_NAME, value='tit').text)
news_link.append(driver.find_element(by=By.CLASS_NAME, value='tit').get_attribute('href'))
for i in range(1,3):
    for j in range(1,4):
        news_title.append(driver.find_element(by=By.XPATH, value='//*[@id="boxApp"]/div[1]/div[2]/ul['+str(i)+']/li['+str(j)+']/a').text)
        news_link.append(driver.find_element(by=By.XPATH, value='//*[@id="boxApp"]/div[1]/div[2]/ul['+str(i)+']/li['+str(j)+']/a').get_attribute('href'))

news = pd.DataFrame(data=news_link,index=news_title)

kospi = driver2.find_element(by=By.XPATH, value='//*[@id="boxIndexes"]/div[1]/span[1]/strong').text + " " + \
driver2.find_element(by=By.XPATH, value='//*[@id="boxIndexes"]/div[1]/span[1]/p[1]').text + " " + \
driver2.find_element(by=By.XPATH, value='//*[@id="boxIndexes"]/div[1]/span[1]/p[2]').text

kosdaq = driver2.find_element(by=By.XPATH, value='//*[@id="boxIndexes"]/div[2]/span[1]/strong').text + " " + \
driver2.find_element(by=By.XPATH, value='//*[@id="boxIndexes"]/div[2]/span[1]/p[1]').text + " " + \
driver2.find_element(by=By.XPATH, value='//*[@id="boxIndexes"]/div[2]/span[1]/p[2]').text

driver.close()
driver2.close()

today = datetime.utcnow().strftime('%Y-%m-%d')
exchange_JPY = fdr.DataReader('JPY/KRW', start=today, end=today) #pytest -> warnings
exchange_USD = fdr.DataReader('USD/KRW', start=today, end=today)
exchange_EUR = fdr.DataReader('EUR/KRW', start=today, end=today) #유로

JPY_To_KRW = 100 * exchange_JPY['Close'][0]
USD_To_KRW = exchange_USD['Close'][0]
EUR_To_KRW = exchange_EUR['Close'][0]

class Ui_pjMain(object):
    def stock_market_color(self):
        if '+' in kospi: self.kospi.setStyleSheet('color: red;')
        else: self.kospi.setStyleSheet('color: blue;')

        if '+' in kosdaq: self.kosdaq.setStyleSheet('color: red;')
        else: self.kosdaq.setStyleSheet('color: blue;')

    def selectstock(self):
        _translate = QtCore.QCoreApplication.translate
        Cop_Id = pjScrap.findCopId(self.select_stock.toPlainText()) # 사용자가 검색한 주식데이터의 종목코드를 반환
        if Cop_Id is False :
            messagebox.showinfo("알림", "주식 검색 결과가 없습니다.")
        else :
            X_train, X_test, y_train, y_test, y_pred, closeStock, realStock, futureFrame10, futureFrame30, stockData30, todayClose, tomorrow_pred, realStock, r2 , stockData = pjMachine.learnData(Cop_Id)
            stockDf = stockData[['SK_DATE', 'SK_OPEN', 'SK_HIGH', 'SK_LOW', 'SK_CLOSE', 'SK_VOLUME']]
            stockDf.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']  # 열 이름 변경

            stockDf['Date'] = pd.to_datetime(stockDf['Date'])
            stockDf.set_index('Date', inplace=True)
            self.fig.clear()  # 기존 그래프 지우기
            axes = self.fig.add_subplot(111)
            mpf.plot(stockDf[-100:], type='candle', style='yahoo', ylabel='Price', ax=axes)
            self.canvas.draw()
            self.predicted_value.clear()
            self.treeWidget.clear()

            # 10일 뒤의 예측데이터를 treewidget 정렬
            for date, value in zip(futureFrame10.index, futureFrame10.values) :
                __sortingEnabled = self.predicted_value.isSortingEnabled()
                item = QtWidgets.QTreeWidgetItem(self.predicted_value)
                item.setText(0, _translate("pjMain", date.strftime('%Y-%m-%d')))
                item.setText(1, _translate("pjMain", str(round(value[0], 2))))
                item.setText(2, _translate("pjMain", str(round(value[1], 2))))
                stockData30 = stockData30[::-1]

            # 실제 30일 주식 데이터 treewidget 정렬
            for date, value in zip(stockData30.index, stockData30.values) :
                __sortingEnabled = self.treeWidget.isSortingEnabled()
                self.treeWidget.setSortingEnabled(False)
                item = QtWidgets.QTreeWidgetItem(self.treeWidget)
                item.setText(0, _translate("pjMain", date.strftime('%Y-%m-%d')))
                item.setText(1, _translate("pjMain", str(round(value[0], 2))))
                item.setText(2, _translate("pjMain", str(round(value[1], 2))))
                item.setText(3, _translate("pjMain", str(round(value[2], 2))))
                item.setText(4, _translate("pjMain", str(round(value[3], 2))))
                self.treeWidget.setSortingEnabled(__sortingEnabled)
                stockData30 = stockData30[::-1]

            self.yester_stock.setText("어제의 주식 : " + str(todayClose.values[0][0]))
            self.pre_today_stock.setText("전일비(예측값) : " + str(tomorrow_pred[0]))
            self.reslut_today_stock.setText("오늘의 주식 : " + str(realStock))
            self.result_stock.setText("정확도 : " + str(r2*100))

    def setupUi(self, pjMain):
        pjMain.setObjectName("pjMain")
        pjMain.setEnabled(True)
        pjMain.resize(1600, 900)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(pjMain.sizePolicy().hasHeightForWidth())
        pjMain.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(login_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        pjMain.setWindowIcon(icon)
        pjMain.setStyleSheet("background-color:rgb(249,247,230);\n"
"selection-background-color:rgb(0, 0, 0);")
        pjMain.setProperty("pjMain", "")
        self.centralwidget = QtWidgets.QWidget(pjMain)
        self.centralwidget.setObjectName("centralwidget")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(50, 140, 1500, 700))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(13)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setAutoFillBackground(False)
        self.frame.setStyleSheet("background-color:rgb(240,246,232);\n"
"selection-background-color:rgb(255,255,255);")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.select_stock = QtWidgets.QPlainTextEdit(self.frame)
        self.select_stock.setGeometry(QtCore.QRect(24, 40, 251, 25))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Highlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Highlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Highlight, brush)
        self.select_stock.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("나눔고딕")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.select_stock.setFont(font)
        self.select_stock.setAcceptDrops(True)
        self.select_stock.setStyleSheet("background-color:rgb(255,255,255);\n"
"selection-background-color:rgb(255,255,255);\n"
"border-color:rgb(52,111,1);\n"
"border-style:solid;\n"
"border-width:0.5px;")
        self.select_stock.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.select_stock.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.select_stock.setObjectName("select_stock")
        self.search_button = QtWidgets.QToolButton(self.frame)
        self.search_button.setGeometry(QtCore.QRect(280, 40, 40, 25))
        self.search_button.clicked.connect(self.selectstock)

        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(32, 110, 17))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(32, 110, 17))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(32, 110, 17))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Highlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(32, 110, 17))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(32, 110, 17))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(32, 110, 17))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Highlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(32, 110, 17))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(32, 110, 17))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(32, 110, 17))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Highlight, brush)
        self.search_button.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("맑은 고딕")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.search_button.setFont(font)
        self.search_button.setStyleSheet("background-color:rgb(32,110,17);\n"
"selection-background-color:rgb(255,255,255);\n"
"color:rgb(255,255,255);")
        self.search_button.setObjectName("search_button")
        self.news = QtWidgets.QListWidget(self.frame)
        self.news.setGeometry(QtCore.QRect(25, 69, 291, 171))
        self.news.setStyleSheet("background-color:rgb(255,255,255);\n"
"selection-background-color:rgb(255,255,255);\n"
"border-color:rgb(52,111,1);\n"
"border-style:solid;\n"
"border-width:0.5px;")
        self.news.setObjectName("news")
        item = QtWidgets.QListWidgetItem()
        self.news.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.news.addItem(item)
        self.predicted_value = QtWidgets.QTreeWidget(self.frame)
        self.predicted_value.setGeometry(QtCore.QRect(593, 50, 261, 191))
        self.predicted_value.setMinimumSize(QtCore.QSize(100, 30))
        self.predicted_value.setMaximumSize(QtCore.QSize(16777215, 231))
        self.predicted_value.setSizeIncrement(QtCore.QSize(0, 30))
        self.predicted_value.setBaseSize(QtCore.QSize(200, 30))
        self.predicted_value.setStyleSheet("border-color:rgb(0,0,0);\n"
"border-style:solid;\n"
"border-width:0.5px;\n"
"background-color:rgb(255,255,255);\n"
"selection-background-color:rgb(255,255,255);\n"
"height:35;")
        self.predicted_value.setLineWidth(100)
        self.predicted_value.setMidLineWidth(100)
        self.predicted_value.setAlternatingRowColors(True)
        self.predicted_value.setIconSize(QtCore.QSize(100, 30))
        self.predicted_value.setTextElideMode(QtCore.Qt.ElideMiddle)
        self.predicted_value.setAutoExpandDelay(2)
        self.predicted_value.setIndentation(0)
        self.predicted_value.setUniformRowHeights(False)
        self.predicted_value.setAllColumnsShowFocus(True)
        self.predicted_value.setHeaderHidden(False)
        self.predicted_value.setExpandsOnDoubleClick(False)
        self.predicted_value.setColumnCount(3)
        self.predicted_value.setObjectName("predicted_value")
        self.predicted_value.headerItem().setText(0, "날짜")
        self.predicted_value.headerItem().setTextAlignment(0, QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.predicted_value.headerItem().setFont(0, font)
        self.predicted_value.headerItem().setBackground(0, QtGui.QColor(231, 225, 217))
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.predicted_value.headerItem().setForeground(0, brush)
        self.predicted_value.headerItem().setTextAlignment(1, QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.predicted_value.headerItem().setFont(1, font)
        self.predicted_value.headerItem().setBackground(1, QtGui.QColor(231, 225, 217))
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.predicted_value.headerItem().setForeground(1, brush)
        self.predicted_value.headerItem().setTextAlignment(2, QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setFamily("맑은 고딕")
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.predicted_value.headerItem().setFont(2, font)
        self.predicted_value.headerItem().setBackground(2, QtGui.QColor(231, 225, 217))
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.predicted_value.headerItem().setForeground(2, brush)
        item_0 = QtWidgets.QTreeWidgetItem(self.predicted_value)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.NoBrush)
        item_0.setBackground(1, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
        brush.setStyle(QtCore.Qt.NoBrush)
        item_0.setForeground(1, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.NoBrush)
        item_0.setForeground(2, brush)
        self.predicted_value.header().setVisible(True)
        self.predicted_value.header().setCascadingSectionResizes(False)
        self.predicted_value.header().setDefaultSectionSize(75)
        self.predicted_value.header().setHighlightSections(False)
        self.predicted_value.header().setMinimumSectionSize(30)
        self.predicted_value.header().setStretchLastSection(False)
        self.yester_stock = QtWidgets.QLabel(self.frame)
        self.yester_stock.setGeometry(QtCore.QRect(340, 60, 230, 21))
        font = QtGui.QFont()
        font.setFamily("맑은 고딕")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.yester_stock.setFont(font)
        self.yester_stock.setStyleSheet("background-color: rgb(255, 255, 255)")
        self.yester_stock.setObjectName("yester_stock")
        self.pre_today_stock = QtWidgets.QLabel(self.frame)
        self.pre_today_stock.setGeometry(QtCore.QRect(340, 110, 230, 21))
        font = QtGui.QFont()
        font.setFamily("맑은 고딕")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.pre_today_stock.setFont(font)
        self.pre_today_stock.setStyleSheet("background-color: rgb(255, 255, 255)")
        self.pre_today_stock.setObjectName("pre_today_stock")
        self.reslut_today_stock = QtWidgets.QLabel(self.frame)
        self.reslut_today_stock.setGeometry(QtCore.QRect(340, 160, 230, 21))
        font = QtGui.QFont()
        font.setFamily("맑은 고딕")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.reslut_today_stock.setFont(font)
        self.reslut_today_stock.setStyleSheet("background-color: rgb(255, 255, 255)")
        self.reslut_today_stock.setObjectName("reslut_today_stock")
        self.result_stock = QtWidgets.QLabel(self.frame)
        self.result_stock.setGeometry(QtCore.QRect(340, 210, 230, 21))
        font = QtGui.QFont()
        font.setFamily("맑은 고딕")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.result_stock.setFont(font)
        self.result_stock.setStyleSheet("background-color: rgb(255, 255, 255)")
        self.result_stock.setObjectName("result_stock")
        self.treeWidget = QtWidgets.QTreeWidget(self.frame)
        self.treeWidget.setGeometry(QtCore.QRect(880, 50, 591, 640))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeWidget.sizePolicy().hasHeightForWidth())
        self.treeWidget.setSizePolicy(sizePolicy)
        self.treeWidget.setMinimumSize(QtCore.QSize(100, 50))
        self.treeWidget.setMaximumSize(QtCore.QSize(16777215, 671))
        self.treeWidget.setSizeIncrement(QtCore.QSize(30, 30))
        self.treeWidget.setBaseSize(QtCore.QSize(200, 30))
        self.treeWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.treeWidget.setAutoFillBackground(False)
        self.treeWidget.setStyleSheet("border-color:rgb(0,0,0);\n"
"border-style:solid;\n"
"border-width:0.5px;\n"
"background-color:rgb(255,255,255);\n"
"selection-background-color:rgb(255,255,255);\n"
"text-align:center;\n"
"height:35;\n"
"")
        self.treeWidget.setLineWidth(100)
        self.treeWidget.setMidLineWidth(100)
        self.treeWidget.setAlternatingRowColors(True)
        self.treeWidget.setIconSize(QtCore.QSize(100, 30))
        self.treeWidget.setAutoExpandDelay(2)
        self.treeWidget.setIndentation(0)
        self.treeWidget.setUniformRowHeights(False)
        self.treeWidget.setAllColumnsShowFocus(True)
        self.treeWidget.setWordWrap(False)
        self.treeWidget.setHeaderHidden(False)
        self.treeWidget.setExpandsOnDoubleClick(False)
        self.treeWidget.setColumnCount(5)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setTextAlignment(0, QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.treeWidget.headerItem().setFont(0, font)
        self.treeWidget.headerItem().setBackground(0, QtGui.QColor(233, 228, 228))
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.treeWidget.headerItem().setForeground(0, brush)
        self.treeWidget.headerItem().setTextAlignment(1, QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.treeWidget.headerItem().setFont(1, font)
        self.treeWidget.headerItem().setBackground(1, QtGui.QColor(233, 228, 228))
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.treeWidget.headerItem().setForeground(1, brush)
        self.treeWidget.headerItem().setTextAlignment(2, QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.treeWidget.headerItem().setFont(2, font)
        self.treeWidget.headerItem().setBackground(2, QtGui.QColor(233, 228, 228))
        brush = QtGui.QBrush(QtGui.QColor(67, 67, 67))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.treeWidget.headerItem().setForeground(2, brush)
        self.treeWidget.headerItem().setTextAlignment(3, QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.treeWidget.headerItem().setFont(3, font)
        self.treeWidget.headerItem().setBackground(3, QtGui.QColor(233, 228, 228))
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.treeWidget.headerItem().setForeground(3, brush)
        self.treeWidget.headerItem().setTextAlignment(4, QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.treeWidget.headerItem().setFont(4, font)
        self.treeWidget.headerItem().setBackground(4, QtGui.QColor(233, 228, 228))
        brush = QtGui.QBrush(QtGui.QColor(0, 85, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.treeWidget.headerItem().setForeground(4, brush)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        self.treeWidget.header().setVisible(True)
        self.treeWidget.header().setCascadingSectionResizes(False)
        self.treeWidget.header().setDefaultSectionSize(120)
        self.treeWidget.header().setHighlightSections(False)
        self.treeWidget.header().setMinimumSectionSize(100)
        self.treeWidget.header().setSortIndicatorShown(False)
        self.treeWidget.header().setStretchLastSection(False)
        self.canvas = QtWidgets.QGraphicsView(self.frame)
        self.canvas.setGeometry(QtCore.QRect(25, 270, 831, 421))
        self.canvas.setStyleSheet("background-color:rgb(255,255,255);\n"
"selection-background-color:rgb(255,255,255);\n"
"border-color:rgb(52,111,1);\n"
"border-style:solid;\n"
"border-width:0.5px;")
        self.canvas.setObjectName("canvas")
        self.fig = plt.figure()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setGeometry(QtCore.QRect(25, 270, 831, 421))
        self.canvas.setObjectName("canvas")
        self.canvas.setParent(self.frame)
        self.axes = self.fig.add_subplot(111)
        # self.figure.plot()
        self.canvas.draw()



        self.frame_2 = QtWidgets.QFrame(self.frame)
        self.frame_2.setGeometry(QtCore.QRect(330, 50, 251, 191))
        self.frame_2.setStyleSheet("background-color:rgb(255,255,255);\n"
"selection-background-color:rgb(255,255,255);\n"
"border-color:rgb(52,111,1);\n"
"border-style:solid;\n"
"border-width:0.5px;")
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.now_data_2 = QtWidgets.QLabel(self.frame)
        self.now_data_2.setGeometry(QtCore.QRect(400, 5, 121, 31))
        font = QtGui.QFont()
        font.setFamily("Noto Sans KR ExtraBold")
        font.setPointSize(20)
        self.now_data_2.setFont(font)
        self.now_data_2.setObjectName("now_data_2")
        self.now_data_3 = QtWidgets.QLabel(self.frame)
        self.now_data_3.setGeometry(QtCore.QRect(100, 5, 151, 31))
        font = QtGui.QFont()
        font.setFamily("Noto Sans KR ExtraBold")
        font.setPointSize(20)
        self.now_data_3.setFont(font)
        self.now_data_3.setObjectName("now_data_3")
        self.now_data_4 = QtWidgets.QLabel(self.frame)
        self.now_data_4.setGeometry(QtCore.QRect(660, 5, 151, 31))
        font = QtGui.QFont()
        font.setFamily("Noto Sans KR ExtraBold")
        font.setPointSize(20)
        self.now_data_4.setFont(font)
        self.now_data_4.setObjectName("now_data_4")
        self.now_data_5 = QtWidgets.QLabel(self.frame)
        self.now_data_5.setGeometry(QtCore.QRect(1110, 10, 121, 31))
        font = QtGui.QFont()
        font.setFamily("Noto Sans KR ExtraBold")
        font.setPointSize(20)
        self.now_data_5.setFont(font)
        self.now_data_5.setObjectName("now_data_5")
        self.frame_2.raise_()
        self.select_stock.raise_()
        self.search_button.raise_()
        self.news.raise_()
        self.predicted_value.raise_()
        self.pre_today_stock.raise_()
        self.reslut_today_stock.raise_()
        self.result_stock.raise_()
        self.treeWidget.raise_()
        self.canvas.raise_()
        self.yester_stock.raise_()
        self.now_data_2.raise_()
        self.now_data_3.raise_()
        self.now_data_4.raise_()
        self.now_data_5.raise_()
        self.stock_market = QtWidgets.QLabel(self.centralwidget)
        self.stock_market.setGeometry(QtCore.QRect(70, 10, 151, 51))
        font = QtGui.QFont()
        font.setFamily("맑은 고딕")
        font.setPointSize(20)
        self.stock_market.setFont(font)
        self.stock_market.setStyleSheet(f"background-image:url({login_path})")
        self.stock_market.setText("")
        self.stock_market.setPixmap(QtGui.QPixmap(login_path))
        self.stock_market.setScaledContents(True)
        self.stock_market.setObjectName("stock_market")
        self.now_data = QtWidgets.QLabel(self.centralwidget)
        self.now_data.setGeometry(QtCore.QRect(70, 60, 421, 31))
        font = QtGui.QFont()
        font.setFamily("Noto Sans KR ExtraBold")
        font.setPointSize(20)
        self.now_data.setFont(font)
        self.now_data.setObjectName("now_data")
        self.project_title = QtWidgets.QLabel(self.centralwidget)
        self.project_title.setGeometry(QtCore.QRect(500, 20, 201, 31))
        font = QtGui.QFont()
        font.setFamily("Noto Sans KR ExtraBold")
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.project_title.setFont(font)
        self.project_title.setObjectName("project_title")
        self.kospi = QtWidgets.QLabel(self.centralwidget)
        self.kospi.setGeometry(QtCore.QRect(500, 60, 361, 21))
        font = QtGui.QFont()
        font.setFamily("Noto Sans KR ExtraBold")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.kospi.setFont(font)
        self.kospi.setObjectName("kospi")
        self.kosdaq = QtWidgets.QLabel(self.centralwidget)
        self.kosdaq.setGeometry(QtCore.QRect(500, 85, 360, 28))
        font = QtGui.QFont()
        font.setFamily("Noto Sans KR SemiBold")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.kosdaq.setFont(font)
        self.kosdaq.setObjectName("kosdaq")
        self.project_title_2 = QtWidgets.QLabel(self.centralwidget)
        self.project_title_2.setGeometry(QtCore.QRect(890, 20, 201, 31))
        font = QtGui.QFont()
        font.setFamily("Noto Sans KR SemiBold")
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.project_title_2.setFont(font)
        self.project_title_2.setObjectName("project_title_2")

        self.USD_img = QtWidgets.QLabel(self.centralwidget)
        self.USD_img.setGeometry(QtCore.QRect(1210, 60, 42, 24))
        self.USD_img.setStyleSheet(f"background-image:url({usa_path})")
        self.USD_img.setText("")
        self.USD_img.setPixmap(QtGui.QPixmap(usa_path))
        self.USD_img.setScaledContents(True)
        self.USD_img.setObjectName("USA_img")

        self.USD = QtWidgets.QLabel(self.centralwidget)
        self.USD.setGeometry(QtCore.QRect(1250, 60, 220, 21))
        font = QtGui.QFont()
        font.setFamily("Noto Sans KR SemiBold")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.USD.setFont(font)
        self.USD.setObjectName("USD")
        ##################################################
        self.KOR_img = QtWidgets.QLabel(self.centralwidget)
        self.KOR_img.setGeometry(QtCore.QRect(890, 60, 42, 24))
        self.KOR_img.setStyleSheet(f"background-image:url({kor_path})")
        self.KOR_img.setText("")
        self.KOR_img.setPixmap(QtGui.QPixmap(kor_path))
        self.KOR_img.setScaledContents(True)
        self.KOR_img.setObjectName("KOR_img")

        self.KOR = QtWidgets.QLabel(self.centralwidget)
        self.KOR.setGeometry(QtCore.QRect(960, 60, 220, 21))
        font = QtGui.QFont()
        font.setFamily("Noto Sans KR SemiBold")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.KOR.setFont(font)
        self.KOR.setObjectName("KOR")
####################################################################

        self.JPY = QtWidgets.QLabel(self.centralwidget)
        self.JPY.setGeometry(QtCore.QRect(960, 85, 220, 28))
        font = QtGui.QFont()
        font.setFamily("Noto Sans KR SemiBold")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.JPY.setFont(font)
        self.JPY.setObjectName("JPY")


        self.JPY_img = QtWidgets.QLabel(self.centralwidget)
        self.JPY_img.setGeometry(QtCore.QRect(890, 85, 42, 24))
        self.JPY_img.setStyleSheet(f"background-image:url({jpn_path})")
        self.JPY_img.setText("")
        self.JPY_img.setPixmap(QtGui.QPixmap(jpn_path))
        self.JPY_img.setScaledContents(True)
        self.JPY_img.setObjectName("JPN_img")

        self.EUR = QtWidgets.QLabel(self.centralwidget)
        self.EUR.setGeometry(QtCore.QRect(1250, 85, 250, 28))
        font = QtGui.QFont()
        font.setFamily("Noto Sans KR SemiBold")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.EUR.setFont(font)
        self.EUR.setObjectName("EUR")

        self.EUR_img = QtWidgets.QLabel(self.centralwidget)
        self.EUR_img.setGeometry(QtCore.QRect(1210, 85, 42, 24))
        self.EUR_img.setStyleSheet(f"background-image:url({eur_path})")
        self.EUR_img.setText("")
        self.EUR_img.setPixmap(QtGui.QPixmap(eur_path))
        self.EUR_img.setScaledContents(True)
        self.EUR_img.setObjectName("EUR_img")

        pjMain.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(pjMain)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1600, 21))
        self.menubar.setObjectName("menubar")
        pjMain.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(pjMain)
        self.statusbar.setObjectName("statusbar")
        pjMain.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(pjMain)
        self.toolBar.setObjectName("toolBar")
        pjMain.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.toolBar_2 = QtWidgets.QToolBar(pjMain)
        self.toolBar_2.setObjectName("toolBar_2")
        pjMain.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar_2)

        self.retranslateUi(pjMain)
        QtCore.QMetaObject.connectSlotsByName(pjMain)

    def retranslateUi(self, pjMain):
        _translate = QtCore.QCoreApplication.translate
        pjMain.setWindowTitle(_translate("pjMain", "MainWindow"))
        self.search_button.setText(_translate("pjMain", "검색"))
        __sortingEnabled = self.news.isSortingEnabled()
        self.news.setSortingEnabled(False)
        self.news.clear()
        for i in range(len(news_title)):
            item = QtWidgets.QListWidgetItem()
            item.setText(news_title[i])
            self.news.addItem(item)
        self.news.setSortingEnabled(__sortingEnabled)
        self.news.itemDoubleClicked.connect(lambda: wb.open(news_link[self.news.currentRow()]))

        self.news.setSortingEnabled(__sortingEnabled)
        self.predicted_value.headerItem().setText(1, _translate("pjMain", "예측값"))
        self.predicted_value.headerItem().setText(2, _translate("pjMain", "전일비"))
        __sortingEnabled = self.predicted_value.isSortingEnabled()
        self.predicted_value.setSortingEnabled(False)

        self.predicted_value.setSortingEnabled(__sortingEnabled)
        self.yester_stock.setText(_translate("pjMain", "어제의주식"))
        self.pre_today_stock.setText(_translate("pjMain", "전일비(예측값)"))
        self.reslut_today_stock.setText(_translate("pjMain", "오늘의 주식"))
        self.result_stock.setText(_translate("pjMain", "정확도"))
        self.treeWidget.headerItem().setText(0, _translate("pjMain", "날짜"))
        self.treeWidget.headerItem().setText(1, _translate("pjMain", "종가"))
        self.treeWidget.headerItem().setText(2, _translate("pjMain", "시가"))
        self.treeWidget.headerItem().setText(3, _translate("pjMain", "고가"))
        self.treeWidget.headerItem().setText(4, _translate("pjMain", "저가"))
        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        self.treeWidget.setSortingEnabled(__sortingEnabled)
        self.now_data_2.setText(_translate("pjMain", "국내 증시"))
        self.now_data_3.setText(_translate("pjMain", "예측 체결가"))
        self.now_data_4.setText(_translate("pjMain", "예측 체결가"))
        self.now_data_5.setText(_translate("pjMain", "일별 시세"))
        self.stock_market.setToolTip(_translate("pjMain", "<html><head/><body><p><br/></p></body></html>"))
        self.now_data.setText(_translate("pjMain", time.strftime("%Y-%m-%d", time.localtime())))
        self.project_title.setText(_translate("pjMain", "오늘의 증시"))
        self.kospi.setText(_translate("pjMain", "코스피 : " + kospi))
        self.kosdaq.setText(_translate("pjMain", "코스닥 : " + kosdaq))
        self.project_title_2.setText(_translate("pjMain", "오늘의 환율"))
        self.USD.setText(_translate("pjMain", "미국 USD : " + str(round(USD_To_KRW, 2))))
        self.JPY.setText(_translate("pjMain", "일본 JPY : " + str(round(JPY_To_KRW, 2))))
        self.EUR.setText(_translate("pjMain", "유럽 EUR : " + str(round(EUR_To_KRW, 2))))
        self.KOR.setText(_translate("pjMain", "한국 KOR : 1000.0" ))
        self.toolBar.setWindowTitle(_translate("pjMain", "toolBar"))
        self.toolBar_2.setWindowTitle(_translate("pjMain", "toolBar_2"))
        self.stock_market_color()