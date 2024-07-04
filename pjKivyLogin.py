#-*- coding: utf-8 -*-
from kivymd.icon_definitions import md_icons
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import (
    MDTextField,
    MDTextFieldLeadingIcon,
    MDTextFieldHintText,
    MDTextFieldHelperText,
    MDTextFieldTrailingIcon,
    MDTextFieldMaxLengthText,
)
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen,ScreenManager
from kivy.core.text import LabelBase
from kivy.uix.popup import Popup
from kivy.graphics import Color
import kivy
kivy.require('1.11.1')
from kivy.config import Config
from pjMydb import UserBuilder
import pjMydb
import pjQtUi
from PyQt5.QtWidgets import QApplication
import sys
import re
import kivy.uix.image as Image
import os

if hasattr(sys, '_MEIPASS') :
    base_path = sys._MEIPASS
else :
    base_path = os.path.abspath(".")

font_path = os.path.join(base_path, 'resources', 'fonts', 'NotoSans-ExtraBold.ttf')
font_path2 = os.path.join(base_path, 'resources', 'fonts', 'NotoSansKR-ExtraBold.ttf')
image_path = os.path.join(base_path, 'resources', 'images', 'Loginpage_logo.png')
image_path2 = os.path.join(base_path, 'resources', 'images', 'join_logo.png')

Config.set('kivy', 'keyboard_mode', 'systemandmulti')
Window.clearcolor = (0.9843, 0.9764, 0.9450, 0)
Window.size = (600,850)
LabelBase.register(name='CustomFont',fn_regular=font_path)
LabelBase.register(name='CustomFont',fn_regular=font_path2)

class CustomTextInput(TextInput):
    max_length = 15
    def __init__(self, **kwargs):
        super(CustomTextInput, self).__init__(**kwargs)
        self.font_name = 'CustomFont'
        with self.canvas.before:
            Color(0,0,0,0.8)

    def insert_text(self, substring, from_undo=False):
        if len(self.text) + len(substring) > self.max_length:
            substring = substring[:self.max_length - len(self.text)]
        return super(CustomTextInput, self).insert_text(substring, from_undo=from_undo)

    def set_max_char(self,max_char):
        self.max_length = max_char

class LoginPage(Screen):
    login_field = ObjectProperty(None)
    def __init__(self, **kwargs):
        super(LoginPage, self).__init__(**kwargs)

class JoinPage(BoxLayout):
    join_id_field = ObjectProperty(None)
    join_pass_field = ObjectProperty(None)
    def __init__(self, **kwargs):
        super(JoinPage, self).__init__(**kwargs)

class HelloStock(MDApp):
    current_popup = None
    #로그인 페이지
    def build(self):
        self.theme_cls.primary_palette = "Springgreen"
        global sm
        sm = ScreenManager()
        login_page = LoginPage(name='login')
        sm.add_widget(login_page)

        #로그인 메인 페이지 로고 이미지 노출
        loginimg=Image.Image(source=image_path,pos_hint= {"center_x": .5, "center_y": .85},
                        size_hint=(None,None),size=(400,100))
        login_page.add_widget(loginimg)

        #메인 페이지 로그인 버튼
        login_button = MDButton(
            MDButtonIcon(icon="heart-outline", size=(10,10)),
            MDButtonText(text="Login"),
            style="filled",
            theme_width='Custom',
            height='50px',
            size_hint_x= .3,
            pos_hint={"center_x":0.5, "center_y": 0.35},
            on_press=self.loginPress)
        login_page.add_widget(login_button)

        #메인페이지 회원가입 페이지 이동 버튼
        join_button = MDButton(
            MDButtonIcon(icon="pencil-outline", size=(10, 10)),
            MDButtonText(text="Joinus"),
            style="filled",
            theme_width='Custom',
            height='50px',
            size_hint_x=.3,
            pos_hint={"center_x": 0.5, "center_y": 0.25},
            on_press=self.joinPress)
        login_page.add_widget(join_button)

        #비회원 전용 페이지 이동 버튼
        Nonmembers_button = MDButton(
            MDButtonIcon(icon="plus", size=(10, 10)),
            MDButtonText(text="Nonmembers"),
            style="filled",
            theme_width='Custom',
            height='50px',
            size_hint_x=.3,
            pos_hint={"center_x": 0.5, "center_y": 0.15},
            on_press=self.nonPress)
        login_page.add_widget(Nonmembers_button)

        id_field = MDTextField(
            MDTextFieldLeadingIcon(icon="account"), 
            MDTextFieldHintText(text="Enter your ID"),
            MDTextFieldHelperText(mode='persistent'),
            MDTextFieldTrailingIcon(icon="information"),
            MDTextFieldMaxLengthText(max_text_length=10),
            mode="outlined",
            size_hint_x=None,
            width='300px',
            height='50px',
            pos_hint={"center_x": 0.5, "center_y": 0.65},
            id = "login_field")
        login_page.login_field = id_field
        login_page.add_widget(id_field)

        password_field = MDTextField(
            MDTextFieldHintText(text="Enter your password"),
            MDTextFieldHelperText(mode="persistent"),
            MDTextFieldTrailingIcon(icon="information"),
            MDTextFieldMaxLengthText(max_text_length=15),
            password=True,
            mode="outlined",
            size_hint_x=None,
            width='300px',
            height='50px',
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            id = "pass_field")
        login_page.pass_field = password_field
        login_page.add_widget(password_field)
        sm.current = 'login'
        return sm

    #회원가입 페이지에서 메인으로 이동하는 함수
    def go_to_main_page(self, instance):
        MDApp.get_running_app().go_to_login()
        self.first_popup.dismiss()

    # 스크린매니저를 통해 로그인 페이지 이동 함수
    def go_to_login(self):
        sm.current = 'login'

    #로그인 버튼 클릭 시 DB 내 ID,PW 매칭 작업
    def loginPress(self, instance):
        login_id = self.root.get_screen('login').login_field.text
        login_pass = self.root.get_screen('login').pass_field.text
        if not login_id or not login_pass :
            return self.show_popup("Error", "Please enter both ID and password")

        #로그인 성공 시 , 메인 대시보드 노출 / 실패 시, Error 팝업 생성
        boolLog = pjMydb.login_user(login_id, login_pass)
        if boolLog == True :
            self.showWindowMain()
        else :
            self.show_popup("Error", "Login failed")


    # 조인 버튼 클릭 시 이동 페이지
    def joinPress(self, instance):
        join_content = JoinPage(orientation='vertical',padding=50,spacing=50)

        joinimg = Image.Image(source=image_path2, pos_hint={"center_x": .5, "center_y": .85},
                          size_hint=(None, None), size=(400, 100))
        join_content.add_widget(joinimg)

        global joinus_id
        joinus_id = CustomTextInput(
            _hint_text='Enter your id',
            input_type='text',
            cursor_color='#000000',
            background_color='#E6E6FA',
            hint_text_color='#000000',
            background_active='#FBF5EF',
            width=400,
            height=50,
            size_hint=(None, None),
            multiline=False,
            pos_hint={"center_x": 0.5, "center_y":0.4})

        join_content.add_widget(joinus_id)

        global joinus_pw
        joinus_pw = CustomTextInput(
            input_type='text',
            password='*',
            _hint_text='Enter your password',
            cursor_color='#000000',
            background_color='#E6E6FA',
            hint_text_color='#000000',
            background_active='#FBF5EF',
            multiline=False,
            width=400,
            height=50,
            size_hint=(None,None),
            pos_hint={"center_x": 0.5, "center_y":0.45})
        joinus_pw.set_max_char(20)
        join_content.add_widget(joinus_pw)

        global joinus_name
        joinus_name = CustomTextInput(
            _hint_text='Enter your name',
            input_type='text',
            cursor_color='#000000',
            background_color='#E6E6FA',
            hint_text_color='#000000',
            background_active='#FBF5EF',
            multiline=False,
            width=400,
            height=50,
            size_hint=(None, None),
            pos_hint={"center_x": 0.5, "center_y":0.55})
        joinus_name.set_max_char(10)
        join_content.add_widget(joinus_name)

        global joinus_add
        joinus_add = CustomTextInput(
            hint_text='Enter your email',
            input_type='mail',
            cursor_color='#000000',
            background_color='#E6E6FA',
            hint_text_color='#000000',
            background_active='#FBF5EF',
            multiline=False,
            width=400,
            height=50,
            size_hint=(None, None),
            pos_hint={"center_x": 0.5, "center_y":0.5})
        joinus_add.set_max_char(25)
        join_content.add_widget(joinus_add)

        joinus_button = MDButton(
            MDButtonIcon(
                icon="pencil-outline",
                size=(10, 10)),

            MDButtonText(
                text="joinus"),

            pos_hint={"center_x": 0.5, "center_y": 0.3},
            size_hint=(0.5, 0.5),
            on_press=self.joinus)
        join_content.add_widget(joinus_button)

        # 버튼 클릭 시 메인 페이지 이동
        back_to_main_button = MDButton(
            MDButtonIcon(
                icon="heart-outline",
                size=(10, 10)),MDButtonText(text="Back to Main Page"), pos_hint={"center_x": 0.5, "center_y": 0.2})
        back_to_main_button.bind(on_press=self.go_to_main_page)
        join_content.add_widget(back_to_main_button)

        self.first_popup = Popup(
            title='Join Us',
            content=join_content,
            size_hint=(None, None),
            size=(600, 850),
            separator_color=[ 0.9764, 0.9568, 0.8745, 0],
            background_color=[0.9843, 0.9764, 0.9450, 1],
            background="Springgreen")
        self.first_popup.open()
        self.current_popup = self.first_popup
        return join_content

    # 회원가입 완료 버튼 클릭 시, 정규표현식 검사 및 데이터 DB 전송
    def joinus(self,instance):
        rexid = re.compile(r'([A-Za-z0-9]{0,10})+')
        rexpass = re.compile(r'^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[!@#$%^&*()])[\w\d!@#$%^&*()]+$')
        rexemail = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        if not re.fullmatch(rexid,joinus_id.text) or not re.fullmatch(rexpass,joinus_pw.text) or not re.fullmatch(rexemail,joinus_add.text):
            self.show_popup("Error", "Join failed")
        else :
            userBuilder = UserBuilder()
            user = (userBuilder.setUsername(joinus_id.text).setPassword(joinus_pw.text).setUname(joinus_name.text).setEmail(joinus_add.text))
            pjMydb.regiUser(user)
            self.current_popup = None
            self.first_popup.dismiss()

    # 로그인, 회원가입 실패시 Error 팝업
    def show_popup(self, title, message):
        content = MDScreen(
            MDLabel(
                text=message,
                halign='center',
                font_size='100sp',
                font_style="Headline",
                pos_hint={"center_x": 0.5, "center_y": 0.5}),
            MDButton(
                MDButtonIcon(icon="heart-outline", size=(10, 10)),
                MDButtonText(text="Close"),
                pos_hint={"center_x": 0.5, "center_y": 0.3},
                on_press=self.close_popup))

        self.second_popup = Popup(
            title=title,
            size=(300, 300),
            content=content,
            separator_color=[0.9764, 0.9568, 0.8745, 1],
            background_color=[0.8980, 0.9098, 0.8862, 1],
            background="Forestgreen")
        self.second_popup.open()
        self.current_popup = self.second_popup
        return content

    # Error 팝업 닫기
    def close_popup(self,instance):
        if self.current_popup:
            self.current_popup.dismiss()
            self.current_popup = None

    # 로그인 성공 시, 이동되는 메인 페이지 연결
    def showWindowMain(self):
        app = QApplication(sys.argv)
        self.main_window = pjQtUi.MainWindow()
        self.main_window.show()
        sys.exit(app.exec_())

    # 비회원 로그인 시, 이동되는 서브 페이지 연결
    def nonPress(self,instance):
        app = QApplication(sys.argv)
        self.main_window = pjQtUi.SubWindow()
        self.main_window.show()
        sys.exit(app.exec_())

if __name__ == '__main__':
    HelloStock().run()
