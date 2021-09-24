import os
import tkinter
import tkinter as tk
from functools import partial
from pathlib import Path
from tkinter import filedialog, scrolledtext
from interface_classes import InterfaceStyle

class FolderChooseButton(tkinter.Button):
    def connect(self,input, method = "directory"):
        self.input = input
        self.method = method
        self.config(command=self.set_to_path)

    def set_to_path(self):
        value = None
        if self.method == 'directory':
            value = filedialog.askdirectory()
        else:
            value = filedialog.askopenfilename()
        self.input.set(value)


class LineFrame(tk.Frame):
    _row = 0

    def __init__(self,m,cnf={}, **kw):
        super(LineFrame,self).__init__(m,cnf, **kw)
        self.clean_up()
        self.needs_update = False

    def _get_row(self):
        self._row += 1
        return self._row-1

    def define_updater(self,to_update):
        self.updaters.append(to_update)

    def clean_up(self):
        self._row = 0
        self.updaters = []
        self.add_component_listeners = []
        self.global_pdx = 0
        self.next_pdx = 0
        self.footer_components = []

    def define_footer_component(self,component,column=0, end=True):
        component_data = {'component':component,'column':column}
        if end:
            self.footer_components.append(component_data)
            return
        self.footer_components.insert(0,component_data)

    def _update_components(self):
        if not self.needs_update: return False

        self.needs_update = False
        self.added_component()

        return True

    def added_c(self, c):
        self.added_component()

    def added_component(self):
        for component in self.footer_components:
            component['component'].grid_forget()
            component['component'].grid(row=self.row,column=component['column'])

        updaters = getattr(self, 'updaters', None)

        if not updaters: return True
        for upd in updaters:
            upd.added_component()

    def remove_component(self, comp):
        comp.grid_forget()
        self.needs_update = True
        self.after(10, self._update_components)

    def add_component(self, comp, row_change=0, column_change=0):
        actual_row = self.row + row_change
        pdx = self.global_pdx + self.next_pdx

        comp.grid(row=actual_row, column=column_change,padx = pdx)

        try:
            s = getattr(comp, 'add_component_listeners')
            s.append(self.added_c)
        except:
            pass

        self.next_pdx = 0
        self.needs_update = True
        self.after(10, self._update_components)

        for to_update in self.add_component_listeners:
            to_update(comp)



    row = property(_get_row)


class ScrolledFrame(LineFrame):

    def __init__(self, f, w=800, h=500, two_dimensions=False):
        self.frame = tk.Frame(f)
        frame = self.frame
        try:
            getattr(self, "destroy_children")
        except:
            self.destroy_children = []
        f.add_component(frame)
        self.scroll_canvas = tk.Canvas(frame)

        self.scroll_canvas.grid()

        LineFrame.__init__(self, self.scroll_canvas, bg='#8ed49f', bd=2)
        self.create_scrollbar(frame, two_dimensions)

        self.change_size(w, h)

        Expander(self.master.master, self.scroll_canvas, 3)

    def create_vbar(self, frame):
        vbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        vbar.grid(row=0, column=1, sticky='ns')
        vbar.config(command=self.scroll_canvas.yview)
        self.scroll_canvas.config(yscrollcommand=vbar.set)

    def create_hbar(self, frame):
        hbar = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
        hbar.grid(row=0, column=0, sticky='sew')
        hbar.config(command=self.scroll_canvas.xview)
        self.scroll_canvas.config(xscrollcommand=hbar.set)

    def create_scrollbar(self, frame, two_dimensions):
        self.create_vbar(frame)
        if two_dimensions:
            self.create_hbar(frame)


    def destroy(self):
        super().destroy()
        self.frame.destroy()

        for child in self.destroy_children:
            child.destroy()

    def change_color(self,color):
        self.scroll_canvas.config(bg=color)

    def change_size(self,w,h):
        self.scroll_canvas.config(width=w, height=h)

    def added_component(self):
        super().added_component()
        self.scroll_canvas.create_window((0, 0), window=self, anchor=tk.NW)
        self.update_idletasks()
        self.scroll_canvas.config(scrollregion=self.scroll_canvas.bbox("all"))


class HorizontalScrolledFrame(ScrolledFrame):

    def create_scrollbar(self, frame, two_dimensions):
        self.create_hbar(frame)

        if two_dimensions:
            self.create_vbar(frame)

    def add_component(self, comp, row_change=0, column_change=0):
        super().add_component(comp, row_change - self._row, column_change+self._row)



class Option(LineFrame):
    def __init__(self,option_parent,name):
        super().__init__(option_parent)
        self.name = name
        self.parent = option_parent
        self.name_text = tk.Label(self, text=name)

        self.remove_button = tk.Button(self, text="remove", command=self.remove)

        self.add_component(self.name_text)
        self.add_component(self.remove_button, -1, +1)

    def remove(self):
        self.parent.options.remove(self.name)
        self.destroy()


class OptionList(ScrolledFrame):

    def __init__(self,m):
        super().__init__(m, 250, 100, True)

        self.option_name = ProperScrolledText(self,height=2)
        self.options = []
        add_button = tk.Button(self, text= "add new option", command=self.add_option)

        self.options_frame = LineFrame(self)

        self.add_component(self.options_frame)
        self.add_component(self.option_name)
        self.add_component(add_button)

    def add_option(self):
        new_name = self.option_name.get()
        new_option = Option(self, new_name)
        self.add_component(new_option)
        self.options.append(new_name)

    def get(self):
        return self.options

    def set(self, names):
        for name in names:
            self.option_name.set(name)
            self.add_option()


class ChildFrame():

    # Parent must define a "start_behaviour" method
    def define_relationship(self,main,main_widget,parent):
        self.back_button = tk.Button(main, text="go back", command= partial(parent.start_behaviour,main,self))
        main.add_component(self.back_button)
        main_widget.destroy_children.append(self.back_button)

        from interface_classes import InterfaceStyle
        InterfaceStyle.colored_button_style.apply_configurations(self.back_button)


# Allows user to modify the height size of an element
class Expander:
    # master -> where to add expander elements
    # controller -> who to expand
    # row_change -> what row the element should be added in
    # divider -> how much to divide expander position to change the
    # height of the element (for some reason that I yet do not understand,
    # frames work perfectly with the position while text inputs need to divide
    # the position by about... 22. Other than that it seems to be consistent,
    # so when adding it to another element just test out the value I guess)
    def __init__(self, master, controller, row_change=0, divider=1):
        self.master = master
        self.init_b = False
        self.controller = controller
        self.divider = divider
        self.move_listening = []
        self.grip = tk.Label(master, bitmap="gray25")
        self.grip.bind("<ButtonPress-1>", self.start_move)
        self.grip.bind("<B1-Motion>", self.do_move)

        self.grip.bind("<ButtonRelease-1>", self.stop_move)

        try:
            self.master.add_component(self.grip,row_change)
        except:
            self.grip.grid(row=row_change)

    def stop_move(self, _event):
        self.grip.place_forget()
        try:
            self.master.added_component()
        except:
            pass
        self.grip.place(x=self.inplace_grip.winfo_x(), y=self.inplace_grip.winfo_y())

    def init_behaviour(self):
        self.init_b = True
        grip_place_grid =  self.grip.grid_info()['row']
        self.grip.grid_forget()

        self.inplace_grip = tk.Label(self.master, bitmap="gray12")
        self.inplace_grip.grid(row=grip_place_grid)

    def start_move(self, event):

        self.grip.x = self.grip.winfo_rootx()
        self.grip.y = event.y

        if not self.init_b:
            self.init_behaviour()

        self.grip.tkraise()

        self.do_move(event)

    def do_move(self, event):
        deltay = event.y - self.grip.y

        y = self.grip.winfo_y() + deltay

        if y < self.controller.winfo_y() + self.controller.winfo_height()*60/100:
            y = self.controller.winfo_y()+ self.controller.winfo_height()*60/100

        self.controller.config(height=(self.grip.winfo_y()-
                                       self.controller.winfo_y())/self.divider)

        self.grip.place(x=self.inplace_grip.winfo_x(), y=y)

        for lis in self.move_listening:
            lis()


class ProperScrolledText(scrolledtext.ScrolledText):
    def __init__(self,m, specifications=None, cnf={}, **kw):
        if not 'width' in cnf:
            cnf['width'] = 15
            cnf['height'] = 5
        super(scrolledtext.ScrolledText,self).__init__(m,cnf,**kw)
        InterfaceStyle.simple_entry_style.apply_configurations(self)
        self.initialize_specifications(specifications)
        exp = Expander(m, self, 2, 22)

        if getattr(self.master, "added_component"):
            exp.move_listening.append(self.master.added_component)

    def initialize_specifications(self, specifications):
        if not specifications:
            return

        if 'folder_reference' in specifications:
            if specifications["folder_reference"]:
                folder_button = FolderChooseButton(self.master)
                folder_button.connect(self)

                self.master.add_component(folder_button, 1, 0)

    def get(self):
        txt = super(scrolledtext.ScrolledText, self).get("1.0",tk.END)
        txt = txt[0:len(txt)-1]
        return txt

    def set(self,new_text):
        if not new_text:
            return
        self.delete('1.0', tk.END)
        self.insert(tk.END,new_text)


class ApplicationFrame(LineFrame):
    def __init__(self,m):
        super().__init__(m)

        self.loader = None


class ArchiveSelector(LineFrame):
    def __init__(self, m, file_path):
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

    def select(self):
        pass

    def on_delete(self):
        pass
