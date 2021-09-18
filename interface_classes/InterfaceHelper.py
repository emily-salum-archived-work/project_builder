import tkinter
import tkinter as tk
from functools import partial
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
        self.updaters = []
        self.global_pdx = 0
        self.next_pdx = 0
        self.footer_components = []
        self.needs_update = False

    def _get_row(self):
        self._row += 1
        return self._row-1

    def define_updater(self,to_update):
        self.updaters.append(to_update)

    def define_footer_component(self,component,column=0, end=True):
        component_data = {'component':component,'column':column}
        if end:
            self.footer_components.append(component_data)
            return
        self.footer_components.insert(0,component_data)

    def _update_components(self):
        if not self.needs_update: return False

        self.needs_update = False
        self._added_component()

        return True

    def _added_component(self):
        for component in self.footer_components:
            component['component'].grid_forget()
            component['component'].grid(row=self.row,column=component['column'])

        updaters = getattr(self, 'updaters', None)

        if not updaters: return True
        for upd in updaters:
            upd._added_component()

    def remove_component(self,comp):
        comp.grid_forget()
        self.needs_update = True
        self.after(10, self._update_components)


    def add_component(self,comp,row_change=0,column_change=0):
        actual_row = self.row + row_change
        pdx = self.global_pdx + self.next_pdx

        comp.grid(row=actual_row, column=column_change,padx = pdx)

        self.next_pdx = 0
        self.needs_update = True
        self.after(10, self._update_components)


    row = property(_get_row)


class ScrolledFrame(LineFrame):


    def destroy(self):
        super().destroy()
        self.frame.destroy()

    def __init__(self, f, w=800, h=500, two_dimensions=False):
        self.frame = tk.Frame(f)
        frame = self.frame
        frame.grid()
        self.scroll_canvas = tk.Canvas(frame)

        self.scroll_canvas.grid()

        LineFrame.__init__(self, self.scroll_canvas, bg='#8ed49f', bd=2)
        vbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        vbar.grid(row=0, column=1, sticky='ns')
        vbar.config(command=self.scroll_canvas.yview)

        if two_dimensions:
            hbar = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
            hbar.grid(row=0, column=1, sticky='e')
            hbar.config(command=self.scroll_canvas.xview)

        self.scroll_canvas.config(yscrollcommand=vbar.set)

        self.change_size(w,h)

    def change_color(self,color):
        self.scroll_canvas.config(bg=color)
    def change_size(self,w,h):
        self.scroll_canvas.config(width=w, height=h)

    def _added_component(self):
        super()._added_component()
        self.scroll_canvas.create_window((0, 0), window=self, anchor=tk.NW)
        self.update_idletasks()
        self.scroll_canvas.config(scrollregion=self.scroll_canvas.bbox("all"))


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
        self.back_button = tk.Button(main_widget, text="go back", command= partial(parent.start_behaviour,main,self))

        main_widget.add_component(self.back_button)

        from interface_classes import InterfaceStyle
        InterfaceStyle.colored_button_style.apply_configurations(self.back_button)


class ProperScrolledText(scrolledtext.ScrolledText):
    def __init__(self,m, specifications = None, cnf={},**kw):
        if not 'width' in cnf:
            cnf['width'] = 15
            cnf['height'] = 5

        super(scrolledtext.ScrolledText,self).__init__(m,cnf,**kw)
        InterfaceStyle.simple_entry_style.apply_configurations(self)
        self.inicialize_specifications(specifications)

    def inicialize_specifications(self, specifications):
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


class ApplicationFrame(tk.Frame):
    def __init__(self,m):
        super().__init__(m)

        self.loader = None
