from abc import ABC, abstractmethod
import tkinter
from interface_classes import InterfaceHelper
from interface_classes import InterfaceStyle


class Maker(ABC, InterfaceHelper.ScrolledFrame, InterfaceHelper.ChildFrame):

    def __init__(self, main, parent, w=500, h=500):
        super().__init__(main,w,h)
        self.define_relationship(main, self, parent)

        button = tkinter.Button(self, text="upload", width=15, command=self.save_data)
        self.add_component(button)
        self.define_footer_component(button)
        InterfaceStyle.positive_button_style.apply_configurations(button)

    @abstractmethod
    def save_data(self):
        pass

    @abstractmethod
    def load_data(self, data):
        pass