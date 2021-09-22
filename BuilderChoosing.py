import tkinter as tk
import interface_classes.InterfaceHelper
from interface_classes import InterfaceHelper
from functools import partial
from interface_classes.InterfaceStyle import standard_button_style as button_style
current_module = __import__(__name__)


new_button_choice = button_style.return_with({'background': '#5f5f5f',
                                              'font_data': button_style.font_data.
                                             return_with({'font_color': '#ffffff'})})

selections = []


def make_selections_from_archives(main_frame, buttons_frame, element_name, archive_names):
    global selections

    selection_frame = make_selection_frame(main_frame)

    get_new_creation_button(buttons_frame, element_name)

    # class reference, This is just so I can shorten a line
    archive_selector_class = interface_classes.InterfaceHelper.ArchiveSelector

    for archive_name in archive_names:
        if not is_correct_archive_name(archive_name):
            continue

        create_single_selector(archive_name, archive_selector_class, element_name, selection_frame)


def create_single_selector(archive_name, archive_selector_class, element_name, selection_frame):
    selection = archive_selector_class(selection_frame, archive_name)
    selection_frame.add_component(selection)
    selection.select_button.config(command=partial(_select_component, selection, element_name))
    remove_button = tk.Button(selection, text='remove', width=30, bd=8, bg="#ff9999",
                              command=partial(remove_component, selection, element_name))
    button_style.apply_configurations(remove_button)
    selection.add_component(remove_button)


def make_selection_frame(main_frame):
    global selections
    selection_frame = InterfaceHelper.HorizontalScrolledFrame(main_frame, 1000, 150)
    main_frame.add_component(selection_frame)
    selections.append(selection_frame)
    selection_frame.global_pdx = 20
    selection_frame.change_color('#88a490')
    return selection_frame


def is_correct_archive_name(archive_name):
    correct_name = True
    if archive_name == '/':
        correct_name = False
    if archive_name == "":
        correct_name = False

    return correct_name


def get_new_creation_button(buttons_frame, element_name):
    global selections
    new_file_text = 'make new ' + element_name
    new_file = tk.Button(buttons_frame, text=new_file_text, width=50,
                         command=partial(make_new, element_name), bg='#484440', fg='#dafadf')
    buttons_frame.add_component(new_file)
    selections.append(new_file)
    new_button_choice.apply_configurations(new_file)


m_canvas = None
canvas: interface_classes.InterfaceHelper.ApplicationFrame = None
mapping = None


def restart_command():
    from builder_helper.builders import builder_data
    builder_data.update_main_data("load_method", None)
    import Main
    restart_interface()
    Main.initialize_application(m_canvas)


def start_behaviour(main_canvas, older_mode = None):
    global canvas
    global selections
    if older_mode and canvas:
        older_mode.destroy()
    global m_canvas

    canvas = main_canvas
    if m_canvas:
        m_canvas.grid()
        return
    global mapping
    mapping = BuilderClassMapping()
    m_canvas = InterfaceHelper.LineFrame(canvas)
    m_canvas.grid()

    create_config_buttons(m_canvas)

    update_selection()


def create_config_buttons(m_canvas):
    reload_button = tk.Button(m_canvas, text="Reload", command=update_selection)
    m_canvas.add_component(reload_button)
    restart_button = tk.Button(m_canvas, text="change load method")
    m_canvas.add_component(restart_button)
    restart_button.config(command=restart_command)


def update_selection():
    global m_canvas
    restart_interface()
    data_loader = canvas.loader
    data_loader.load_control_listing()
    controls = data_loader.controls

    buttons_frame = InterfaceHelper.LineFrame(m_canvas)
    m_canvas.add_component(buttons_frame, 0)
    selections.append(buttons_frame)
    for control_key in controls.keys():
        control = controls[control_key]
        make_selections_from_archives(m_canvas, buttons_frame, control_key, control.names)


def restart_interface():
    for selection in selections:
        selection.destroy()


def _select_component(component, name_selected):

    loader = canvas.loader

    # noinspection PyUnresolvedReferences
    from builder_helper.builders import builder_help
    data = loader.load_data(component.path, builder_help.BuildElement[name_selected.upper()])
    m_canvas.grid_forget()
    global mapping

    select_class = mapping.get_builders(name_selected).select

    select_class(canvas, current_module, data)


def make_new(type):
    m_canvas.grid_forget()
    global mapping
    maker = mapping.get_builders(type).new_select
    maker(canvas, current_module)


def remove_component(component, name):
    component.on_delete()
    component.destroy()

    # noinspection PyUnresolvedReferences
    from builder_helper.builders import builder_help
    m_canvas.master.loader.remove_archive(component.path, builder_help.BuildElement[name.upper()])


class BuilderClassSelection:
    def __init__(self, select, new_select=None):
        self.select = select
        self.new_select = new_select if new_select else select


class BuilderClassMapping:
    def __init__(self):
        # noinspection PyUnresolvedReferences
        from builder_helper.builders import builder_help
        from makers.ProjectMaker import ProjectMaker
        from TemplateChoosing import TemplateChoosing
        from makers.TemplateMaker import TemplateMaker
        from makers.RequirementsMaker import RequirementsMaker
        self.mapper = {builder_help.BuildElement.PROJECT.to_string(): BuilderClassSelection(ProjectMaker, TemplateChoosing),
                       builder_help.BuildElement.TEMPLATE.to_string(): BuilderClassSelection(TemplateMaker),
                       builder_help.BuildElement.REQUIREMENTS.to_string(): BuilderClassSelection(RequirementsMaker),
                       }

    def get_builders(self, element):
        return self.mapper[element]
