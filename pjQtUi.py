from PyQt5.QtWidgets import QMainWindow, QApplication
from pjMain import Ui_pjMain
from pjNologin import Ui_pjSub
from PyQt5.QtGui import QFont,QFontDatabase

class MainWindow(QMainWindow, Ui_pjMain):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def custom_font(font_path):
        font_id=QFontDatabase.applicationFont(font_path)
        font_family=QFontDatabase.applicationFontFamilies(font_id)
        custom_font= QFont(font_family[0])
        QApplication.setFont(custom_font)

class SubWindow(QMainWindow, Ui_pjSub):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def custom_font(font_path):
        font_id = QFontDatabase.applicationFont(font_path)
        font_family = QFontDatabase.applicationFontFamilies(font_id)
        custom_font = QFont(font_family[0])
        QApplication.setFont(custom_font)




