'''
Copyright (C) 2015 masterxeon1001
masterxeon1001@gmail.com

Created by masterxeon1001 and team

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "Hard Ops 8",
    "description": "Hard Ops 8 - V7: Hassium",
    "author": "MX, IS, RF, JM, AR, BF, SE, PL, MKB, CGS, PG, proxe, Adam K, Wazou, Pistiwique, Jacques and you",
    "version": (0, 0, 8, 7),
    "blender": (2, 77, 0),
    "location": "View3D",
    #"warning": "Hard Ops - The Global Bevelling Offensive V 007x",
    "wiki_url": "https://masterxeon1001.com/2016/09/13/hard-ops-8-p4-update/",
    "category": "Object" }


from . import developer_utils
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())

import bpy,bgl,blf
from . registration import register_all, unregister_all

def register():
    bpy.utils.register_module(__name__)
    register_all()
    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))

def unregister():
    bpy.utils.unregister_module(__name__)
    unregister_all()
    print("Unregistered {}".format(bl_info["name"]))
