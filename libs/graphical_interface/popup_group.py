from ..database import DBMuziek
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.lang.builder import Builder
from .utils import ErrorPopup

Builder.load_file('libs/graphical_interface/popup_group.kv')


class PopupGroup(Popup):
    def __init__(self, db: DBMuziek, update_data=None, **kwargs):
        super(PopupGroup, self).__init__(**kwargs)
        self._db = db
        self._update_id = update_data["group_id"] if update_data else None
        if update_data:
            self.update_data(update_data)
            self.title = "Modify a group"
        else:
            self.title = "Create a group"

    def submit_form(self):
        data = self.validate_form()
        if data:
            with self._db.connection:
                if self._update_id:
                    self._db.update_group(self._update_id, data["members"])
                else:
                    self._db.create_group(**data)
            self.dismiss()

    def validate_form(self):
        buffer = {}
        name_input = self.ids.name_input
        members_list = self.ids.members_list

        if not name_input.text:
            ErrorPopup("No name provided.")
            return None
        elif not self._update_id and self._db.get_group(name_input.text):
            ErrorPopup("The group already exists.")
            return None

        buffer["name"] = name_input.text

        members = [self.ids[f"member{i + 1}"].text
                   for i in range(members_list.counter)
                   if self.ids[f"member{i + 1}"].text]

        if not members:
            ErrorPopup("No members provided.")
            return None

        buffer["members"] = members

        return buffer

    def add_member_field(self):
        members_list = self.ids.members_list

        member_input = TextInput(multiline=False)
        members_list.add_widget(member_input, 1)

        members_list.counter += 1
        self.ids[f"member{members_list.counter}"] = member_input
        self.ids.members_list_container.size_hint = (1, members_list.counter + 1)

    def update_data(self, data):
        self.ids.name_input.text = data["group_name"]
        self.ids.name_input.disabled = True
        members_list = self.ids.members_list

        if isinstance(data["members"], str):
            members = data["members"].split(",")
        else:
            members = data["members"]

        for i, member in enumerate(members, 1):
            if i > members_list.counter:
                self.add_member_field()

            self.ids[f"member{i}"].text = member
