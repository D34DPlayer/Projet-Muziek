from kivy.app import App
from kivy.uix.label import Label


class MainWindow(App):
    def build(self):
        return Label(text='Main window', font_size='100sp')
