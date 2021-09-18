import tkinter as tk
from tkinter import filedialog

from interface_classes import InterfaceHelper
import os

from builder_helper.builders.builder_help import BuildElement
from tkinter import *
from PIL import Image, ImageTk
from interface_classes.InterfaceHelper import FolderChooseButton
from makers.BuilderElements import Maker

class ProjectMaker(Maker):
    def __init__(self, main, parent, data, template=None):
        super().__init__(main, parent, 1000)
        self.main = main
        self.properties = {}


        self._row += 1
        pr = PropertyInput(self, {'type': "ProperScrolledText", 'name': "Archive Name",
                                              'base_value':""})
        self.add_component(pr)

        self.properties["path_name"] = pr


        if template:
            self.template = template["name"]
            self._use_template(template)
        if data:
            self.load_data(data)

        self.call_processes = tk.BooleanVar()
        self.call_processes.set(True)
        processes_check = tk.Checkbutton(self, text="call processes")
        processes_check.config(variable=self.call_processes)
        self.add_component(processes_check)

    def save_data(self):
        data = {}
        values = self.get_property_values()
        data["properties"] = values
        data["template"] = self.template

        data["name"] = values['path_name']
        self.main.loader.save_data(data, BuildElement.PROJECT)

        from builder_helper.builders import builder_data
        from builder_helper.builders import builder_help

        builder_data.update_main_data("latest_project", data['name'])
        builder_help.update_archive(data['template'],
                                    BuildElement.TEMPLATE,
                                    "on_delete",
                                    {"method" : 'remove_archive',
                                     "name": data["name"],
                                     "control" : BuildElement.PROJECT.to_string()}
                                    , "append")

        if self.call_processes.get():
            self.call_automated_processes(data)

    def load_data(self, data):
        self.template = data["template"]
        self._use_template(self.main.loader.load_data(data["template"], BuildElement.TEMPLATE))
        for k in data["properties"]:
            self.properties[k].set(data["properties"][k])

    def _use_template(self,template):
        self._add_properties(template)

        template_states = list(template["states"])
        in_value = ""
        if not len(template_states) == 0:
            in_value = template_states[0]
            self.string_state = tk.StringVar(self, in_value)
            self.state_option = OptionMenu(self, self.string_state,*template_states)
            self.state_option.grid(row=1)
        
    def _add_properties(self,temp):
        for property in temp["properties"]:
            pr = PropertyInput(self, property)
            self.add_component(pr)
            self.properties[property["name"]] = pr
            print(property)
            self.make_folder_button(property,pr)
            self.make_file_button(property,pr)

    def make_folder_button(self, property,input):
        if 'folder_reference' not in property: return
        if not property['folder_reference']: return
        self.make_choose_button(input, "directory")

    def make_file_button(self, property, input):
        if 'file_reference' not in property: return
        if not property['file_reference']: return
        self.make_choose_button(input, "file")

    def make_choose_button(self, input, method):
        choose_folder_button = FolderChooseButton(self, text=f"choose {method}", width=15)
        choose_folder_button.connect(input, method)
        self.add_component(choose_folder_button, -1)


    def get_property_values(self):
        values = {}
        for k in self.properties.keys():
            values[k] = self.properties[k].get()
        return values

    def call_automated_processes(self, data):

        try:
            getattr(self,'string_state')
        except:
            return

        loader = self.main.loader
        f = loader.load_data(data["template"], BuildElement.TEMPLATE)

        all_requirements = f["states"][self.string_state.get()]
        all_processes = []
        for requirement in all_requirements:
            d = loader.load_data(requirement, BuildElement.REQUIREMENTS)
            all_processes.append(d["exe_path"])

        for process_path in all_processes:
            os.system(process_path)


class PropertyInput(InterfaceHelper.LineFrame):
    def __init__(self,m,data, dict={}):
        super().__init__(m)
        self.p = None
        d_type = data["type"]
        self.d_type = d_type

        if d_type == "ProperScrolledText":
            self.add_component(tk.Label(self, text=data["name"]))
            self.p = InterfaceHelper.ProperScrolledText(self, height=10)
            self.add_component(self.p)
        if d_type == "Checkbutton":
            c = tk.Checkbutton(self,text=data["name"])
            self.add_component(c)

            self.p = tk.BooleanVar()
            c.config(variable=self.p, text=data["name"])
        if d_type == "OptionMenu":
            self.add_component(tk.Label(self, text=data["name"]))
            option_string = tk.StringVar()
            options = data["options"]
            if not len(options) == 0:
                option_string.set(options[0])
                options = tk.OptionMenu(self, option_string,options[0], *options[1:])
                self.add_component(options)
                self.p = option_string
        if d_type == "OptionList":
            self.add_component(tk.Label(self,text=data["name"]))
            options_listing = InterfaceHelper.OptionList(self)
            self.add_component(options_listing)
            self.p = options_listing


        if d_type == "image":
            self.p = tk.Label(self)
            self.add_component(self.p)

            self.path = None
            self.add_component(tk.Button(self,command=self.choose_image,width=40))



        if "base_value" in data:
            self.set(data["base_value"])



    def choose_image(self,path=None):
        if path is None:
            path = filedialog.askopenfilename()
        load = Image.open(path)
        self.path=path
        render = ImageTk.PhotoImage(load)
        self.p.config(image=render)

    def set(self, value):
        d_type = self.d_type

        if d_type == "image":
            self.choose_image(value)
        else:
            self.p.set(value)

    def get(self):
        res = None

        d_type = self.d_type

        if d_type == "image":
            res = self.path
        else:
            res = self.p.get()

        return res
