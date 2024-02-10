import bpy
import textwrap

from bpy.types import PropertyGroup
from bpy.props import BoolProperty, IntProperty

from ... utility import names


def draw(preference, context, layout):
    col = layout.column()
    for name, url in weblinks:
        col.operator("wm.url_open", text=name).url = url


weblinks = [
    ("Documentation",           "http://hardops-manual.readthedocs.io/en/latest/"),
    ("Youtube",                 "https://www.youtube.com/user/masterxeon1001/"),
    ("Gumroad",                 "https://gumroad.com/l/hardops/"),
    ("Hard Ops 9 Videos",       "https://www.youtube.com/playlist?list=PL0RqAjByAphEUuI2JDxIjjCQtfTRQlRh0"),
    ("Hard Ops 8 Videos",       "https://www.youtube.com/playlist?list=PL0RqAjByAphGEVeGn9QdPdjk3BLJXu0ho"),
    ("Version 9 Notes",         "https://masterxeon1001.com/2018/06/04/boxcutter-6-8-8-ghostscythe/"),
    ("Version 8 Notes",         "https://masterxeon1001.com/2017/02/10/hard-ops-0087-hassium-update/")
]
