from kivy.lang.builder import Builder
from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup

from ..database import DBMuziek
from ..downloader import SongDownloader
from .popup_group import PopupGroup
from .utils import ErrorPopup

Builder.load_file('libs/graphical_interface/popup_song.kv')


class PopupSong(Popup):
    def __init__(self, db: DBMuziek, update_data=None, **kwargs):
        super(PopupSong, self).__init__(**kwargs)
        self._db = db

        params = {"group_id": update_data["group_id"],
                  "group_name": update_data["group_name"]} if update_data else None
        self.ids["group_input"] = GroupDropdown(self._db, params)
        self.ids.group_container.add_widget(self.ids["group_input"])

        self.add_featuring_field()

        self._update_id = update_data["song_id"] if update_data else None
        if update_data:
            self.update_data(update_data)
            self.title = "Modify a song"
        else:
            self.title = "Create a song"

    def submit_form(self):
        dl = SongDownloader(Logger)
        data = self.validate_form()
        if data:
            with self._db.connection:
                if self._update_id:
                    data["song_id"] = self._update_id
                    name = data.pop("name")
                    g_id = data.pop("group_id")
                    self._db.update_song(**data)

                    if dl.is_downloaded(data["song_id"]):
                        dl.update_metadata(self._db.get_song(name, g_id))
                else:
                    self._db.create_song(**data)
            self.dismiss()

    def add_featuring_field(self):
        featuring_list = self.ids.featuring_list

        featuring_input = GroupDropdown(self._db, text="<Choice>")
        featuring_list.add_widget(featuring_input, 1)

        featuring_list.counter += 1
        self.ids[f"feat{featuring_list.counter}"] = featuring_input
        self.ids.featuring_list_container.size_hint = (1, featuring_list.counter + 1)

    def validate_form(self):
        downloader = SongDownloader(Logger)

        buffer = {}
        name_input = self.ids.name_input
        featuring_list = self.ids.featuring_list
        group_input = self.ids.group_input
        genre_input = self.ids.genre_input
        link_input = self.ids.link_input

        if group_input.choice is None:
            ErrorPopup('No group was provided.')
            return None

        buffer["group_id"] = group_input.choice

        if not name_input.text:
            ErrorPopup("No name provided.")
            return None
        elif not self._update_id and self._db.get_song(name_input.text, group_input.choice):
            ErrorPopup("The song already exists.")
            return None

        buffer["name"] = name_input.text

        if not genre_input.text:
            ErrorPopup("No genre provided.")
            return None

        buffer["genre"] = genre_input.text

        if not link_input.text:
            ErrorPopup("No link provided.")
            return None
        elif not (video_info := downloader.fetch_song(link_input.text)):
            ErrorPopup("The link provided isn't valid.")
            return None

        buffer["link"] = link_input.text
        buffer["duration"] = video_info["duration"]

        featuring = [self.ids[f"feat{i + 1}"].choice
                     for i in range(featuring_list.counter)
                     if self.ids[f"feat{i + 1}"].choice and
                     self.ids[f"feat{i + 1}"].choice != group_input.choice]

        buffer["featuring"] = list(set(featuring))

        return buffer

    def update_data(self, data):
        self.ids.name_input.text = data["song_name"]
        self.ids.name_input.disabled = True
        self.ids.genre_input.text = data["genre"]
        self.ids.link_input.text = data["link"]
        self.ids.group_input.update_data(data)
        featuring_list = self.ids.featuring_list

        for i, featuring in enumerate(data["featuring"], 1):
            if i > featuring_list.counter:
                self.add_featuring_field()

            self.ids[f"feat{i}"].update_data(featuring)


class GroupDropdown(Button):
    def __init__(self, db: DBMuziek, default=None, **kwargs):
        super(GroupDropdown, self).__init__(**kwargs)

        self.dropdown = DropDown()

        self.choice = None
        self.text = "<Choice>"

        self.update_data(default)

        self._db = db
        self.groups = None
        self.update_groups()

        self.bind(on_release=self.open)
        self.dropdown.bind(on_select=lambda _, btn: self.on_select(btn))

    def update_data(self, data):
        if data:
            self.choice = data["group_id"]
            self.text = data["group_name"]
            self.disabled = True

    def reset_choice(self, dd):
        if dd:
            dd.dismiss()
        self.text = "<Choice>"
        self.choice = None

    def update_groups(self):
        self.groups = self._db.get_groups()
        self.dropdown.clear_widgets()

        btn = Button(text="<Choice>", size_hint_y=None, height=44)
        btn.bind(on_release=lambda _: self.reset_choice(self.dropdown))
        self.dropdown.add_widget(btn)

        for group in self.groups:
            btn = GroupButton(text=group["group_name"], size_hint_y=None, height=44)
            btn.set_id(group["group_id"])
            btn.bind(on_release=self.dropdown.select)

            self.dropdown.add_widget(btn)

        btn = Button(text="+", size_hint_y=None, height=44)
        btn.bind(on_release=lambda _: summon_popup_group(self._db, self.dropdown))
        self.dropdown.add_widget(btn)

    def open(self, btn):
        self.update_groups()
        self.dropdown.open(btn)

    def on_select(self, btn):
        self.text = btn.text
        self.choice = btn.group_id


class GroupButton(Button):
    def __init__(self, **kwargs):
        super(Button, self).__init__(**kwargs)

        self.group_id = None

    def set_id(self, i):
        self.group_id = i


def summon_popup_group(db: DBMuziek, dd: DropDown):
    dd.dismiss()
    PopupGroup(db).open()
