from builder_helper import LoadMethodOptions
from interface_classes import InterfaceHelper
import Main
from builder_helper.builders import builder_data
import tkinter


class InterfaceChooseMethod(InterfaceHelper.LineFrame):

    def __init__(self,m):
        super().__init__(m)

        self.option_var = tkinter.StringVar(self)

        Loaders = list(LoadMethodOptions.load_methods.keys())

        first_loader = Loaders[0]
        self.option_var.set(first_loader)

        options = tkinter.OptionMenu(self, self.option_var, first_loader,
                                     *Loaders[1:])
        self.add_component(options)

        select = tkinter.Button(self,text='select',command= self.choose_option)
        self.add_component(select)



    def choose_option(self):
        builder_data.update_main_data("load_method", self.option_var.get())
        self.destroy()
        Main.initialize_application(self.master)