from interface_classes import InterfaceHelper, InterfaceStyle
import os
import tkinter
from pathlib import Path
from functools import partial
import makers.ProjectMaker
import builder_choosing
from builder_helper.builders.builder_help import BuildElement


class ArchiveOption(InterfaceHelper.LineFrame):
    def __init__(self,m,file_path):
        super().__init__(m)

        self.global_pdx = 90
        self.path = file_path
        path_without_suffix = Path(file_path).with_suffix('')

        self.clean_filename = os.path.basename(path_without_suffix)

        select_label = tkinter.Label(self, text=f"Select {self.clean_filename}")
        self.add_component(select_label)
        InterfaceStyle.use_style(select_label)
        self.select_button = tkinter.Button(self, text='select', width=30, bd=8,
                  bg="#99ff99")
        self.add_component(self.select_button)
        InterfaceStyle.standard_button_style.apply_configurations(self.select_button)

    def _select(self):
        # Make Project _use_template with template path
        pass

    def _on_delete(self):
        pass



class TemplateChoosing(InterfaceHelper.ScrolledFrame, InterfaceHelper.ChildFrame):
    def __init__(self,m,parent):
        super().__init__(m,1000)
        self.m = m
        self.define_relationship(m,self,parent)

        choose_text = tkinter.Label(self, text="Choose template to use")
        InterfaceStyle.main_text_style.apply_configurations(choose_text)
        self.add_component(choose_text)

        options = m.loader.controls[BuildElement.TEMPLATE.to_string()].names

        for option in options:
            selection = ArchiveOption(self, option)
            self.add_component(selection)
            selection.select_button\
                .config(command=partial(self.open_project_maker,option))

    def open_project_maker(self, template_name):
        self.destroy()
        data = self.m.loader.load_data(template_name, BuildElement.TEMPLATE)

        makers.ProjectMaker.ProjectMaker(self.m, builder_choosing, None, data)