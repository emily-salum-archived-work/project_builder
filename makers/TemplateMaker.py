from interface_classes import InterfaceHelper
import tkinter as tk
from tkinter import ttk
import BuildField
from builder_helper.builders.builder_help import BuildElement

import component_configuration
from pathlib import Path
import os
from makers.BuilderElements import Maker

configuration = None
class TemplateMaker(Maker):
    def __init__(self, main: InterfaceHelper.ApplicationFrame, parent, template_data = None):
        super().__init__(main, parent, 1000)

        self.main = main
        self.exe_path_list = AutomatedProcessList(main,self, self)
        self.add_component(self.exe_path_list)

        self.add_component(tk.Label(self, text="template name"))
        self.name = InterfaceHelper.ProperScrolledText(self, height=3)
        self.add_component(self.name)

        self.data_list = InterfaceHelper.LineFrame(self)
        self.add_component(self.data_list)
        self.data_list.define_updater(self)

        self.data_type = tk.StringVar()

        self.data_type.set(InterfaceHelper.ProperScrolledText.__name__)

        self.opts=ttk.Combobox(self, textvariable=self.data_type)
        self.opts["values"] = component_configuration.input_types_as_strings()
        self.opts["state"]="readonly"
        self.add_component(self.opts)

        b = tk.Button(self, text="add new data", width=50,
                      command=self._add_new_data)
        self.add_component(b)

        self.added_processes = []

        for n in component_configuration.input_types_as_strings():
            component_configuration.field_groups[n] = []

        if template_data:
            self.load_data(template_data)

    def save_data(self):
        dr = {}
        properties = []
        for group in component_configuration.field_groups.keys():
            for field in component_configuration.field_groups[group]:
                properties.append(field.get())

        dr["properties"] = properties

        dr["name"] = self.name.get()

        dr["states"] = self.exe_path_list.get_states()

        self.main.loader.save_data(dr, BuildElement.TEMPLATE)

    def load_data(self,data):
        states = data['states']
        for state in states.keys():
            state_frame = self.exe_path_list._add_state(state)

            for process in states[state]:
                p_frame = state_frame.processes[process]
                p_frame.is_on.set(True)
                p_frame.turn(False)
                p_frame.check_preference()

        self.name.set(data["name"])
        for v in data["properties"]:
            d = self._add_data(v["type"], v)



    def _remove_process(self,path):
        self.added_processes.remove(path)

        data = self._load_requirements(path)

        for v in data["fields"]:
            for field in configuration.field_groups[v["type"]]:
                if field.values["name"].get() == v["name"]:
                    configuration.field_groups[v["type"]].remove(field)
                    field.destroy()
                    break

        for c in data["components"]:
            component_data = {'type': c["type"], 'name': c["name"]}
            for t in c["supported_types"].keys():
                if not c["supported_types"][t]:
                    continue
                configuration.input_options[t].remove(component_data)

                for f in configuration.field_groups[t]:
                    f.remove_input(component_data)


    def _load_requirements(self,requirements_name):

        data = self.main.loader.load_data(requirements_name, BuildElement.REQUIREMENTS)
        if not data: return {'fields':[],'components':[]}

        return data

    def _new_process(self,folder_path,add_fields=True):
        if folder_path in self.added_processes:
            return
        self.added_processes.append(folder_path)


        data = self._load_requirements(folder_path)

        if add_fields:
            for v in data["fields"]:
                n = self._add_data(v["type"])
                n.values["name"].set(v["name"])

        for c in data["components"]:
            self._add_component(c)


    def _add_component(self,c):

        for t in c["supported_types"].keys():
            if not c["supported_types"][t]:
                continue
            component_configuration.input_options[t].append(c)

            for f in component_configuration.field_groups[t]:
                f.make_input(c)

    def _add_data(self,data_type, data={}):
        t = BuildField.make_build_field(self, self.data_list,
                                        data_type, [component_configuration.field_groups[data_type]], data)
        return t


    def remove_field(self,field):
        component_configuration.field_groups[field.inp_type].pop(field.ind)

    def _add_new_data(self):
        t = self.opts.get()
        return self._add_data(t)

class AutomatedProcessList(InterfaceHelper.LineFrame):

    def __init__(self, main, m, scroll_frame):
        super(AutomatedProcessList, self).__init__(m)
        add_state_button = tk.Button(self, text="add state", width=30,
                  command=self._add_state)
        self.main = main
        self.add_component(add_state_button)

        self.scroll_frame = scroll_frame

        self.list_of_processes = {}
        self.current_list = None

        self.new_state_name = tk.Entry(self)
        self.add_component(self.new_state_name)

        self.string_state = tk.StringVar()
        self.string_state.trace("r", self.change_state_v)
        self.state_box = None

    def _add_state(self,name=None):
        if not name:
            name = self.new_state_name.get()

        new_state = ProcessesFrame(self.main,self,self.scroll_frame)
        self.list_of_processes[name] = new_state

        if not self.state_box:
            opts = []
            self.string_state.set(name)
            self.state_box = tk.OptionMenu(self, self.string_state, name, *opts,)
            self.add_component(self.state_box,-1)
        else:
            self.state_box['menu'].add_command(label=name, command=tk._setit(self.string_state, name))
        self.change_state(new_state)

        return new_state

    def change_state_v(self,*args):
        name = self.string_state.get()
        if name == '':
            return
        self.change_state(self.list_of_processes[name])

    def change_state(self, new_state):
        if self.current_list:
            self.current_list.frame.grid_forget()
            self._row -= 1
        self.current_list = new_state
        self.add_component(self.current_list.frame)

    def get_states(self):
        states = {}
        for state in self.list_of_processes.keys():
            states[state] = {}
            processes_array = self.list_of_processes[state].processes_array
            for process in processes_array:
                if process.is_on.get():
                    states[state][process.path] = True

        return states

    def _get_paths(self):
        paths = {}

        for process_frame_name in self.list_of_processes.keys():
            paths[process_frame_name] = []
            process_frame = self.list_of_processes[process_frame_name]
            for p in process_frame.processes:
                if not p.is_on.get():
                    continue
                paths[process_frame_name].append(p.res)

        return paths


class ProcessesFrame(InterfaceHelper.ScrolledFrame):
    def __init__(self, main,parent, scroll_frame):
        super(ProcessesFrame, self).__init__(parent, 100, 100)
        self.processes = {}
        self.processes_array = []
        requirement_names = main.loader.controls[BuildElement.REQUIREMENTS.to_string()].names
        self.inicial_grid = self._row

        for process in requirement_names:
            id = self._row - self.inicial_grid
            pr = AutomatedProcess(main,self, scroll_frame,self,process,id)
            self.add_component(pr)
            self.processes[process] = pr
            self.processes_array.append(pr)

class AutomatedProcess(InterfaceHelper.LineFrame):

    def __init__(self,main,f,scroll_frame,owner, path,id):
        self.scroll_frame = scroll_frame
        self.id = id
        super(AutomatedProcess, self).__init__(f)

        self.owner = owner

        self.path = path
        res = path

        self.down_button = tk.Button(self, text="go down", command=self.go_down)
        self.add_component(self.down_button)


        self.is_on = tk.BooleanVar()

        self.check_on = tk.Checkbutton(self, variable=self.is_on,
                                       command=self.turn)
        self.add_component(self.check_on)


        clean_path = os.path.basename(Path(self.path).with_suffix(""))

        self.process_path = tk.Label(self, text=clean_path)
        self.add_component(self.process_path)

        self.up_button = tk.Button(self, text="go up", command=self.go_up)
        self.add_component(self.up_button)

    def check_preference(self):
        _id = self.id
        if _id == 0:
            return

        process_array = self.master.processes_array
        before_me = process_array[_id - 1]
        if before_me.is_on.get():
            return

        self.go_down()
        self.check_preference()

    def go_up(self):
        m = self.master

        if self.id + 1 >= len(m.processes_array):
            return
        _id = self.id
        m.processes_array[_id], m.processes_array[_id + 1] = m.processes_array[_id + 1], m.processes_array[_id]
        self.id += 1
        m.processes_array[_id].id -= 1
        m.processes_array[_id].update_position()
        self.update_position()

    def go_down(self):
        if self.id == 0:
            return
        m = self.master
        _id = self.id
        m.processes_array[_id], m.processes_array[_id - 1] = m.processes_array[_id - 1], m.processes_array[_id]
        self.id -= 1
        m.processes_array[_id].id += 1
        m.processes_array[_id].update_position()
        self.update_position()


    def update_position(self):
        self.grid_forget()
        self.grid(row=self.master.inicial_grid + self.id)

    def turn(self, add_fields=True):
        if not self.is_on.get():
            self.scroll_frame._remove_process(self.path)
            return
        self.scroll_frame._new_process(self.path, add_fields)





