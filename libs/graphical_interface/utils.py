from kivy.lang.builder import Builder
from kivy.uix.popup import Popup

Builder.load_file('libs/graphical_interface/utils.kv')


class ErrorPopup(Popup):
    def __init__(self, error, **kwargs):
        super(ErrorPopup, self).__init__(**kwargs)

        self.ids.text_label.text = error
        self.title = "ERROR"
        self.open()
