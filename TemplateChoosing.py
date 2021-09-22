from interface_classes import InterfaceHelper, InterfaceStyle
import tkinter
from functools import partial
import makers.ProjectMaker
import BuilderChoosing
from builder_helper.builders.builder_help import BuildElement

from interface_classes.InterfaceHelper import ArchiveSelector


class TemplateChoosing(InterfaceHelper.ScrolledFrame, InterfaceHelper.ChildFrame):
    def __init__(self, m, parent):
        super().__init__(m, 1000)
        self.m = m
        self.define_relationship(m, self, parent)

        choose_text = tkinter.Label(self, text="Choose template to use")
        InterfaceStyle.main_text_style.apply_configurations(choose_text)
        self.add_component(choose_text)

        options = m.loader.controls[BuildElement.TEMPLATE.to_string()].names

        for option in options:
            selection = ArchiveSelector(self, option)
            self.add_component(selection)
            selection.select_button\
                .config(command=partial(self.open_project_maker,option))

    def open_project_maker(self, template_name):
        self.destroy()
        data = self.m.loader.load_data(template_name, BuildElement.TEMPLATE)

        makers.ProjectMaker.ProjectMaker(self.m, BuilderChoosing, None, data)