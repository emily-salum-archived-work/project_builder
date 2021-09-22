import tkinter as tk
import re
import os

from interface_classes.InterfaceHelper import ApplicationFrame

import sys
sys.path.insert(0, "..")

# noinspection PyUnresolvedReferences
from builder_helper.builders import builder_data
# noinspection PyUnresolvedReferences
from builder_helper import LoadMethodOptions
import BuilderChoosing
current_module = __import__(__name__)


def start_window():
    global window
    width = window.winfo_screenwidth()
    height = window.winfo_screenheight()
    window.geometry("%dx%d" % (width, height))
    window.title('project builder')


def find_exe_in_folder(folder_path):
    for sub_path in os.listdir(folder_path):

        if re.search('exe', sub_path):
            return folder_path + "/" +sub_path
        if os.path.isdir(sub_path):
            exe_in_path = find_exe_in_folder(sub_path)
            if exe_in_path:
                return exe_in_path
    return None


def initialize_application(main_canvas):

    load_method = builder_data.get_from_main_data("load_method")

    # noinspection PyUnresolvedReferences
    from builder_helper.builders import builder_help

    if not load_method:
        from InterfaceChooseMethod import InterfaceChooseMethod
        interface = InterfaceChooseMethod(main_canvas)
        interface.grid()
        return

    loader = builder_help.get_loader()
    data_was_loaded = loader.load()

    if not data_was_loaded:
        from loader_interfaces.Connector import Connector
        connector = Connector(main_canvas, loader.loading_requirements())
        connector.grid()
        return

    main_canvas.loader = loader
    BuilderChoosing.start_behaviour(main_canvas)


if __name__ == "__main__":
    window = tk.Tk()
    start_window()
    main_canvas = ApplicationFrame(window)
    main_canvas.grid()
    initialize_application(main_canvas)
    window.mainloop()


