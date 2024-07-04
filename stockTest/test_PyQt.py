import pytest

from PyQt5 import QtCore
from pjMain import Ui_pjMain
#import pyqt 사용중인 클래스 임폴트 후 테스트
import logging
logger = logging.getLogger(__name__)

@pytest.fixture
def app(qtbot):
    test_hello_app = Ui_pjMain.setupUi()
    qtbot.addWidget(test_hello_app)

    return test_hello_app


def test_label(app):
    assert app.text_label.text() == "Hello World!"


def test_label_after_click(app, qtbot):
    qtbot.mouseClick(app.button, QtCore.Qt.LeftButton)
    assert app.text_label.text() == "Changed!"