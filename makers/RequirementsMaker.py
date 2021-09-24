import component_configuration
from interface_classes import InterfaceHelper
from tkinter import ttk
import tkinter as tk
from builder_helper.builders.builder_help import BuildElement
from makers import BuildField
from makers.BuilderElements import Maker
import Main

class RequirementsMaker(Maker):

    def __init__(self, main, parent, data=None):

        self.start_buttons(main, parent)
        super().__init__(main, parent, 1000)
        self.loaded = not data == None
        self.main = main

        process_label = tk.Label(main, text="process name")
        main.add_component(process_label)
        self.destroy_children.append(process_label)

        self.name = InterfaceHelper.ProperScrolledText(main, width=20, height=4)
        main.add_component(self.name)
        self.destroy_children.append(self.name)

        path_label = tk.Label(main, text="path to program")
        main.add_component(path_label)
        self.destroy_children.append(path_label)

        self.program_path = InterfaceHelper.ProperScrolledText(main, width=20, height=4)
        main.add_component(self.program_path)
        self.destroy_children.append(self.program_path)

        self.program_path_button = InterfaceHelper.FolderChooseButton(main, width=20, text="program folder")
        main.add_component(self.program_path_button,-1)
        self.destroy_children.append(self.program_path_button)

        self.program_path_button.connect(self.program_path)

        self.exe_path = InterfaceHelper.ProperScrolledText(main, width=20, height=4)
        main.add_component(self.exe_path)

        self.exe_path_button = InterfaceHelper.FolderChooseButton(main, width=20, text="get path to exe")
        main.add_component(self.exe_path_button)
        self.exe_path_button.connect(self.exe_path, "file")

        self.exe_auto_button = tk.Button(main, text = "attempt to auto-find", command=self.search_exe)
        main.add_component(self.exe_auto_button)

        self.fields_frame = InterfaceHelper.HorizontalScrolledFrame(self, 600, 400, True)
        self.fields_frame.define_updater(self)
        self.add_component(self.fields_frame)

        self.components_frame = InterfaceHelper.ScrolledFrame(self,300,200)
        self.components_frame.define_updater(self)
        self.add_component(self.components_frame)

        self.reqs = dict()
        self.reqs["fields"] = []
        self.reqs["components"] = []

        self.data_type = tk.StringVar()
        self.data_type.set(InterfaceHelper.ProperScrolledText.__name__)
        self.opts = ttk.Combobox(self, textvariable=self.data_type)
        self.opts["values"] = component_configuration.input_types_as_strings()
        self.opts["state"] = "readonly"
        self.define_footer_component(self.opts, 0, False)
        self.add_component(self.opts)
        add_field = tk.Button(self, width=20,
                             command=self._add_new_field, text="add new field")
        self.add_component(add_field)
        self.define_footer_component(add_field, 0, False)



        add_component = tk.Button(self.components_frame, width=20,
               command= self._add_new_component
                                  ,text="new component")
        add_component.grid(row=self.components_frame.row)

        if data:
            self.load_data(data)

    def search_exe(self):

        self.exe_path.set(Main.find_exe_in_folder(self.program_path.get()))

    def save_data(self):
        new_data = {}
        r_fields = []
        for ent in self.reqs["fields"]:
            r_fields.append(ent.get())
        new_data["fields"] = r_fields

        r_components = []
        for ent in self.reqs["components"]:
            r_components.append(ent.get_properties())
        new_data["components"] = r_components

        new_data['program_path'] = self.program_path.get()
        new_data['exe_path'] = self.exe_path.get()
        new_data['name'] = self.name.get()

        self.main.loader.save_data(new_data, BuildElement.REQUIREMENTS)

    def load_data(self, data):
        self.name.set(data['name'])
        self.program_path.set(data['program_path'])
        self.exe_path.set(data['exe_path'])
        for f in data["fields"]:
            field = self._add_new_field()
            for v in f.keys():
                field.set_data(v, f[v])

        for f in data["components"]:
            component = self._add_new_component()
            component.load_properties(f)

    def _add_new_field(self):
        new_field = BuildField.make_build_field(self, self.fields_frame, self.opts.get(),
                                                [self.reqs["fields"]])
        new_field.define_updater(self.fields_frame)
        return new_field

    def remove_field(self,inp):
        self.reqs['fields'].remove(inp)

    def _add_new_component(self):
        new_component = Property(self.components_frame,self,"components")
        self.components_frame.add_component(new_component)
        self.reqs["components"].append(new_component)

        self._update_components()
        return new_component


class Component(InterfaceHelper.LineFrame):
    def __init__(self, frame):
        super(InterfaceHelper.LineFrame, self).__init__(frame)

        self.accepted_types = {}
        self.accepted_types_frame = InterfaceHelper.ScrolledFrame(self, 120, 50)

        for type in component_configuration.input_types_as_strings():
            inp = tk.Checkbutton(self.accepted_types_frame, width=15)
            self.accepted_types_frame.add_component(inp)
            v = tk.BooleanVar()
            self.accepted_types[type] = v
            inp.config(variable=v, text=type)

    def set(self, new_values):
        for k in new_values.keys():
            self.accepted_types[k].set(new_values[k])

    def get(self):
        rs = {}
        for k in self.accepted_types.keys():
            rs[k] = self.accepted_types[k].get()
        return rs


class Property(InterfaceHelper.LineFrame):
    def __init__(self,frame, control, inp_type):
        super(Property, self).__init__(frame)
        self.control = control
        self.inp_type = inp_type
        self.properties = {}


        if inp_type == "components":
            self.properties["supported_types"] = Component(self)
            self.add_component(self.properties["supported_types"])

        types = component_configuration.input_types_as_strings()
        self.var_type = tk.StringVar(self,types[0])
        self.p_type = tk.OptionMenu(self, self.var_type,
                                    *types[1:])
        self.var_type.trace('w', self.update_build_field)
        self.p_type.config(width=20)
        self.add_component(self.p_type)
        self.properties["type"] = self.var_type

        self.build_field = None
        self.update_build_field()

        self.remove_button = tk.Button(self, text="remove", command=self.remove)

        self.add_component(self.remove_button)

    def update_build_field(self,*_args):
        if self.build_field:
            self.build_field.grid_forget()
        self.build_field = BuildField.make_builder_field_with_single_owner(self,
                                                                           self.var_type.get())

        self.properties['build_field'] = self.build_field


    def remove(self):
        self.control.reqs[self.inp_type].remove(self)
        self.destroy()


    def load_properties(self, p):
        for k in p.keys():
            self.properties[k].set(p[k])

    def get_properties(self):
        props = {}

        for k in self.properties.keys():
            props[k] = self.properties[k].get()

        return props