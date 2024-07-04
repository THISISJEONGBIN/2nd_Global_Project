import pytest
from kivy.clock import Clock
from kivymd.uix.button import MDButton, MDButtonText
from kivy.uix.popup import Popup
from pjStock0702.pjKivyLogin import HelloStock

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
        #print(container.children)
        if isinstance(child, MDButton):
            for Subchild in child.children:
                if isinstance(Subchild, MDButtonText) and Subchild.text == text:
                    return child
    return None


def test_login_button_click(sm, app):
    login_page = sm
    """
    for child in login_page.children:
        print(child)
        #print(f"Child: {child}, Type: {type(child)}")
        if isinstance(child,MDButton):
            for Subchild in child.children:
                print(Subchild)
            #print(f"SubChild: {Subchild}, Type: {type(Subchild)},Text:{getattr(Subchild, 'text', None)}")
    """
    login_button = find_button_with_text(sm, 'Login')
    assert login_button is not None, "Login button not found"
    login_page.login_field.text = 'test_id'
    login_page.pass_field.text = 'test_password'
    login_button.on_press()
    #login_button.trigger_action(duration=0.1)
    Clock.tick()
    assert app.build().current == 'login'

def join_button_with_text(container) :
    for child in container.children:
        if isinstance(child, MDButton):
            for subchild in child.children:
                if subchild.text == "joinus" :
                    return child

def test_join_button_click(sm, app):
    login_page = sm
    #print(sm)
    join_button = find_button_with_text(sm, 'Joinus')
    #close_button = join_fail_close_button(sm, 'Joinus')
    assert join_button is not None, "Join button not found"
    join_button.on_press()
    Clock.tick()
    popup = app.joinPress(None)
    assert isinstance(popup, Popup), "Popup not found"
    assert popup.title == 'Join Us'

def test_join_fields(sm, app):
    join_page = app.joinPress(None).content
    join_button = join_button_with_text(join_page)
    join_page.children[2].text = 'test'
    join_page.children[3].text = 'test_password'
    join_page.children[4].text = 'test_name'
    join_page.children[5].text = 'test@example.com'
    join_button.trigger_action(duration=0.1)
    Clock.tick()
    assert app.build().current == 'login'