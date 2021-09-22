import tkinter as tk

import os
from . import BuildProperty
from builder_helper.builders.builder_help import BuildElement
from tkinter import *
from makers.BuildProperty import PropertyInput
from makers.BuilderElements import Maker


class ProjectMaker(Maker):
    def __init__(self, main, parent, data, template=None):
        self.start_buttons(main, parent)
        super().__init__(main, parent, 1000)

        self.main = main
        self.properties = {}

        self._row += 1
        self.make_name_property()

        self.start_loading(data, template)

        self.call_processes = tk.BooleanVar()
        self.processes_check_button(main)

    def make_name_property(self):
        pr = PropertyInput(self, {'type': "ProperScrolledText", 'name': "Archive Name",
                                  'base_value': ""})
        self.add_component(pr)
        self.properties["name"] = pr

    def start_loading(self, data, template):
        if template:
            self.template = template["name"]
            self._use_template(template)
        if data:
            self.load_data(data)

    def processes_check_button(self, main):
        self.call_processes.set(True)
        processes_check = tk.Checkbutton(main, text="call processes")
        processes_check.config(variable=self.call_processes)
        main.add_component(processes_check)
        self.destroy_children.append(processes_check)

    def save_data(self):
        data = {}
        values = self.get_property_values()
        data["properties"] = values
        data["template"] = self.template

        data["name"] = values['name']
        self.main.loader.save_data(data, BuildElement.PROJECT)

        self.save_process(data)

        if self.call_processes.get():
            self.call_automated_processes(data)

    def save_process(self, data):
        from builder_helper.builders import builder_data
        from builder_helper.builders import builder_help

        builder_data.update_main_data("latest_project", data['name'])
        builder_help.update_archive(data['template'],
                                    BuildElement.TEMPLATE,
                                    "on_delete",
                                    {"method": 'remove_archive',
                                     "name": data["name"],
                                     "control": BuildElement.PROJECT.to_string()}
                                    , "append")

    def load_data(self, data):
        self.template = data["template"]
        self._use_template(self.main.loader.load_data(data["template"], BuildElement.TEMPLATE))
        for k in data["properties"]:
            self.properties[k].set(data["properties"][k])

    def _use_template(self,template):
        self._add_properties(template)
        self.load_states(template)

    def load_states(self, template):
        if 'states' not in template:
            return

        template_states = list(template["states"])

        if len(template_states) == 0:
            return

        in_value = template_states[0]
        self.string_state = tk.StringVar(self, in_value)
        self.state_option = OptionMenu(self, self.string_state, *template_states)
        self.state_option.grid(row=1)

    def _add_properties(self,temp):
        for property_data in temp["properties"]:
            pr = BuildProperty.make_property_input(self, property_data)
            self.add_component(pr)
            self.properties[property_data["name"]] = pr

    def get_property_values(self):
        values = {}
        for k in self.properties.keys():
            values[k] = self.properties[k].get()
        return values

    def call_automated_processes(self, data):

        try:
            getattr(self, 'string_state')
        except:
            return
        state_name = self.string_state.get()

        loader = self.main.loader
        template = loader.load_data(data["template"], BuildElement.TEMPLATE)

        if state_name not in template["states"]:
            return

        all_requirements = template["states"][state_name]
        all_processes = []
        for requirement in all_requirements:
            d = loader.load_data(requirement, BuildElement.REQUIREMENTS)
            all_processes.append(d["exe_path"])

        for process_path in all_processes:
            os.system(process_path)


