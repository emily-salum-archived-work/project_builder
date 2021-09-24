import tkinter as tk
from interface_classes.InterfaceHelper import FolderChooseButton
from interface_classes import InterfaceHelper


def make_property_input(m, property_data):
    pr = PropertyInput(m, property_data)

    make_folder_button(property_data, pr)
    make_file_button(property_data, pr)

    return pr


def make_folder_button(property, input):
    if 'folder_reference' not in property: return
    if not property['folder_reference']: return
    make_choose_button(input, "directory")


def make_file_button(property, input):
    if 'file_reference' not in property: return
    if not property['file_reference']: return
    make_choose_button(input, "file")


def make_choose_button(input, method):
    choose_folder_button = FolderChooseButton(input, text=f"choose {method}", width=15)
    choose_folder_button.connect(input, method)
    input.add_component(choose_folder_button, -1)



class PropertyInput(InterfaceHelper.LineFrame):
    def __init__(self, m, data, dict={}):
        super().__init__(m)
        self.p = None
        d_type = data["type"]
        self.d_type = d_type

        self.input_makers[d_type](self, data)

        if "base_value" in data:
            self.set(data["base_value"])

    def set(self, value):
        self.p.set(value)

    def get(self):
        res = self.p.get()
        return res

    def make_text_name(self, name):
        text = tk.Label(self, text=name)
        self.add_component(text)

    def make_text_input(self, data):
        self.make_text_name(data['name'])
        self.p = InterfaceHelper.ProperScrolledText(self, height=10)
        self.add_component(self.p)

    def make_check_button(self, data):
        c = tk.Checkbutton(self, text=data["name"])
        self.add_component(c)

        self.p = tk.BooleanVar()
        c.config(variable=self.p, text=data["name"])

    def make_option_menu(self, data):
        self.make_text_name(data['name'])
        option_string = tk.StringVar()
        options = data["options"]
        if not len(options) == 0:
            option_string.set(options[0])
            options = tk.OptionMenu(self, option_string, options[0], *options[1:])
            self.add_component(options)
            self.p = option_string

    def make_option_list(self, data):
        self.make_text_name(data['name'])
        options_listing = InterfaceHelper.OptionList(self)
        self.add_component(options_listing)
        self.p = options_listing

    input_makers = {
        "ProperScrolledText": make_text_input,
        "Checkbutton": make_check_button,
        "OptionMenu": make_option_menu,
        "OptionList": make_option_list
    }
