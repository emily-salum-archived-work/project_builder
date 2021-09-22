from abc import ABC, abstractmethod
import tkinter
from interface_classes import InterfaceHelper
from interface_classes import InterfaceStyle


class Maker(ABC, InterfaceHelper.HorizontalScrolledFrame, InterfaceHelper.ChildFrame):

    def __init__(self, main, parent, w=500, h=500):
        super().__init__(main, w, h, True)

    def start_buttons(self, main, parent):
        self.destroy_children = []
        self.define_relationship(main, self, parent)
        button = tkinter.Button(main, text="upload", width=15, command=self.save_data)
        main.add_component(button)
        main.define_footer_component(button)
        self.destroy_children.append(button)
        InterfaceStyle.positive_button_style.apply_configurations(button)

    @abstractmethod
    def save_data(self):
        pass

    @abstractmethod
    def load_data(self, data):
        pass