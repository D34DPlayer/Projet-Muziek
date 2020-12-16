from kivy.uix.popup import Popup


class ErrorPopup(Popup):
    def __init__(self, error, **kwargs):
        super(ErrorPopup, self).__init__(**kwargs)

        self.ids.text_label.text = error
        self.title = "ERROR"
        self.open()


class InfoPopup(Popup):
    def __init__(self, error, **kwargs):
        super(InfoPopup, self).__init__(**kwargs)

        self.ids.text_label.text = error
        self.title = "INFO"
        self.open()
