
from interface_classes import InterfaceHelper
import Main
import tkinter
from builder_helper.builders import builder_data

inputs = {"text": InterfaceHelper.ProperScrolledText}


class Connector(InterfaceHelper.LineFrame):
    def __init__(self, m, loader_requirements):
        super().__init__(m)

        self.inputs = {}
        for requirement in loader_requirements:
            text = requirement['name'] if 'name' in requirement else requirement['id']
            self.add_component(tkinter.Label(self, text=text))

            input_class = inputs[requirement['input']]
            input_instance = input_class(self, requirement)
            self.inputs[requirement['id']] = input_instance
            self.add_component(input_instance)

        finish_button = tkinter.Button(self, text="Confirm", command=self.finish_connection)
        self.add_component(finish_button)

    def finish_connection(self):
        for input_id in self.inputs:
            builder_data.update_main_data(input_id, self.inputs[input_id].get())
        Main.initialize_application(self.master)
        self.destroy()

