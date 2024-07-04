import pytest
from kivy.clock import Clock
from kivymd.uix.button import MDButton, MDButtonText
from kivy.uix.popup import Popup
from pjStock0702.pjKivyLogin import HelloStock
from kivy.uix.widget import Widget
import time
import logging
logger = logging.getLogger(__name__)

@pytest.fixture(scope='module')

def app():
    app = HelloStock()
    app.build()
    yield app
    app.stop()


@pytest.fixture
def sm(app):
    return app.build().get_screen('login')

def find_button_with_text(container, text):
    for child in container.children:
        if isinstance(child, MDButton):
            print(child)
            for Subchild in child.children:
                if Subchild.text == text:
                    return child
    return None

def test_login_button_click(sm, app):
    login_button = find_button_with_text(sm, 'Login')
    assert login_button is not None, "Login button not found"
    print(login_button) # 지금 로그인 버튼에 오는 오브젝트랑 child에서 넘어오는 오브젝트랑 동일한지 봐야함
    Clock.tick()
    print(app.current_popup)


# close 버튼 확인
def find_button_show_text(container, text):
    for child in container.children :
        if isinstance(child, MDButton):
            return child

def join_button_with_text(container) :
    for child in container.children:
        if isinstance(child, MDButton):
            for subchild in child.children:
                #print(subchild.text)
                if subchild.text == "joinus" :
                    return child



    # login_page = sm
    # login_button = find_button_with_text(sm, 'Login')
    # assert login_button is not None, "Login button not found"
    # login_page.login_field.text = 'suk123dsad'
    # login_page.pass_field.text = '1234'
    #
    # print(app.current_popup)
    # #login_button.trigger_action(duration=0.1)
    # Clock.tick()
    # assert app.build().current == 'login'

def test_show_button_with_text(sm,app):
    show_button = find_button_show_text(app.show_popup("error", "meeaaa"), 'Close')
    assert show_button is not None, "Show button not found"
    show_button.dispatch('on_press')


def test_join_button_click(sm, app):
    join_button = find_button_with_text(sm, 'Joinus')
    assert join_button is not None, "Join button not found"
    join_button.dispatch('on_press')

def test_login(sm, app) :
    login_page = sm
    assert login_page is not None, "Login Page not found"

def test_join(sm, app):
    join_page = app.joinPress(None)

    joinId = join_page.children[5]
    joinPw = join_page.children[4]
    joinNa = join_page.children[3]
    joinAd = join_page.children[2]

    joinId.text = "asd123"
    joinPw.text = "123"
    joinNa.text = "한석희"
    joinAd.text = "Email321@naver.com"

    join_button = join_button_with_text(join_page)
    assert join_button is not None, "join button not found"
    join_button.dispatch('on_press')
    Clock.tick()
    assert app.current_popup is not None, "Join Fails"




