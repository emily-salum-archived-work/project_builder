import tkinter as tk

import makers.BuildProperty
from interface_classes import InterfaceHelper
import Main
from component_configuration import input_options


def make_build_field(scroll, owner, type, groups=[],data={}):

    field = BuilderField(scroll, owner, type)
    scroll.add_component(field)

    for key in data.keys():
        field.set_data(key, data[key])

    for array in groups:
        array.append(field)

    return field

def make_builder_field_with_single_owner(scroll_owner, type,groups=[],data={}):
    return make_build_field(scroll_owner,scroll_owner,type,groups,data)


# holds the components a field has (name,base value,etc)
class BuilderField(InterfaceHelper.LineFrame):
    def __init__(self, scroll_frame, m, typ):
        self.values = {}
        self.inputs = {}
        self.scroll_frame = scroll_frame

        self.ind = self.i

        self.i += 1

        self.inp_type = typ
        super(BuilderField, self).__init__(m, bd=1)

        use_inputs = input_options[typ]

        for use_input in use_inputs:

            self.make_input(use_input)
        delete_button = tk.Button(self, text="delete", command=self.remove)
        self.add_component(delete_button)
        self.define_footer_component(delete_button)

        test_field_button = tk.Button(self, text="test", command=self.test)
        self.add_component(test_field_button)

        self.make_space_button()

    def make_space_button(self):
        r_button = tk.Button(self, text="                               ")
        r_button.config(height=1)
        r_button["state"] = tk.DISABLED
        r_button.grid(row=self._row + 1)
        self.define_footer_component(r_button)

    def test(self):
        pr = makers.BuildProperty.make_property_input(self, self.get())

        try:
            self.master.master.add_component(pr, 1,1)
        except AttributeError:
            self.master.add_component(pr, 1,1)

        delete_button = tk.Button(pr, text="delete", command=pr.destroy)

        pr.add_component(delete_button)

    i = 0

    def remove(self):

        self.i -= 1
        self.scroll_frame.remove_field(self)
        self.scroll_frame.remove_component(self)

    def get(self):
        v = {}

        for k in self.values.keys():
            v[k] = self.values[k].get()

        v["type"] = self.inp_type
        return v

    def set(self, data):
        for k in data.keys():
            self.set_data(k, data[k])

    def set_data(self, data_name, data):
        if data_name == "type":
            return

        if data_name in self.values:
            d = self.values[data_name]
            d.set(data)

    var_types = {tk.Checkbutton.__name__: tk.BooleanVar, }

    def remove_input(self, input_data):
        name = input_data["name"]
        input = self.inputs[name]

        input.destroy()
        self.inputs[name] = None
        self.values[name] = None

    def make_input(self, input_data):
        name = input_data["build_field"]["name"]
        if name in self.values.keys():
            return

        inp = makers.BuildProperty.PropertyInput(self, input_data["build_field"])
        self.inputs[name] = inp
        self.values[name] = inp
        self.add_component(inp)
