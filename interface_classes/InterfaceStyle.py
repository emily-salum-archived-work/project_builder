import tkinter
from tkinter.font import Font
from dataclasses import dataclass, field,replace

# Attempt of a quick way to standard the interface while maintaining customization

# quick class to share functions?
class Data:
    def return_with(self, changes):
        new_style = replace(self)
        for change_name in changes.keys():
            new_style.__setattr__(change_name, changes[change_name])
        return new_style




@dataclass
class FontData(Data):
    font: str
    font_size: int
    font_color: str
    font_weight: str = field(default='normal')

@dataclass
class Style(Data):
    font_data: FontData
    background: str = field(default='None')
    bd: int = field(default=0)

    def return_with_font_changed(self,font_changes):
        copy = replace(self)
        copy.font_data = self.font_data.return_with(font_changes)
        return copy

    def apply_configurations(self,component):
        use_style(component,self)

standard_font = FontData("Times New Roman", 14, '#a87ca8','bold')
standard_text_style = Style(standard_font)
standard_button_style = Style(FontData("helvetica",10,'#000000'))
colored_button_style = standard_button_style.return_with({'background':'#30c0a0'})
main_text_style = standard_text_style.return_with_font_changed({'font_size':30,'font_color': "#9fdf9f"})

warning_text = standard_text_style.return_with_font_changed({'font_color':"Red"})

positive_button_style = standard_button_style.return_with\
    ({"bd": 6, "background": '#99ff99'})

simple_entry_style = Style(standard_font.return_with({"font_color": "#B76E87"}), "#FFCEF2",3)

def use_style(component,style=standard_text_style):
    if not style: return
    font = style.font_data
    load_font(component, font)

    if style.background == 'None':
        return
    component.config(bg=style.background, bd = style.bd)


def load_font(component, font):
    if not font: return
    assign_font = Font(family=font.font, weight=font.font_weight, size=font.font_size)
    component.config(font=assign_font)
    component.config(fg=font.font_color)

