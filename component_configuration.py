import tkinter as tk

from interface_classes import InterfaceHelper
import tkinter
from interface_classes.InterfaceHelper import ProperScrolledText

text = InterfaceHelper.ProperScrolledText.__name__
checkbox = tkinter.Checkbutton.__name__
base_components = [{'build_field':{'name': "name", 'type': text}},
                   ]
field_groups = {}
def input_types_as_strings():
    global string_input_types
    global input_types
    if string_input_types is not None:
        return string_input_types

    string_input_types = []
    for inp in input_types:
        string_input_types.append(inp.__name__)

    return string_input_types

string_input_types = None
input_types = (ProperScrolledText, tk.Checkbutton, tk.OptionMenu, InterfaceHelper.OptionList)
string_input_types = input_types_as_strings()


for type in input_types_as_strings():
    field_groups[type] = []
text_inputs = base_components + [
    {'build_field':{'name': "folder_reference", 'type': checkbox}},
    {'build_field':{'name': "file_reference", 'type': checkbox}},
    {'build_field':{'name': "base_value", 'type': text}},
          ]
checkbox_inputs = base_components + [{'build_field':{'name': "base_value", 'type': checkbox}} ]
image_inputs = base_components + []
options_inputs =  base_components + [{'build_field':{'name': "options", 'type': InterfaceHelper.OptionList.__name__}}]
input_options = {text:text_inputs, 'Checkbutton':checkbox_inputs,
                 'OptionMenu':options_inputs, "OptionList": base_components}


def input_class_from_text(name):
    for inp in component_configuration.input_types:
        if inp.__name__ == name:
            return inp
    return None