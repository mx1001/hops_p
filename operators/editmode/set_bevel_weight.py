import bpy
import bmesh
from bpy.props import BoolProperty
from ... preferences import get_preferences


class HOPS_OT_SetEditSharpen(bpy.types.Operator):
    bl_idname = "hops.set_edit_sharpen"
    bl_label = "Hops Set Sharpen"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Mark Ssharp / Unmark Toggle"

    dont_affect_bevel: BoolProperty(name="Don't affect bevel weight",
                                    description="Don't affect bevel weight that was set manually",
                                    default=False)

    @classmethod
    def poll(cls, context):
        object = context.active_object
        return(object.type == 'MESH' and context.mode == 'EDIT_MESH')

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.prop(self, "dont_affect_bevel")

    def execute(self, context):

        obj = bpy.context.object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        bw = bm.edges.layers.bevel_weight.verify()
        cr = bm.edges.layers.crease.verify()

        selected = [e for e in bm.edges if e.select]

        if selected:
            if self.sync_apply_seam(me, selected):
                return {'FINISHED'}
            if self.sync_apply_crease(me, cr, selected):
                return {'FINISHED'}
            if self.sync_apply_sharps(me, selected):
                return {'FINISHED'}

        if not selected:
            for e in bm.edges:
                if e.calc_face_angle(0) >= get_preferences().property.sharpness:
                    if get_preferences().property.sharp_use_crease:
                        e[cr] = 1
                    if get_preferences().property.sharp_use_sharp:
                        e.smooth = False
                    if get_preferences().property.sharp_use_seam:
                        e.seam = True
                    if get_preferences().property.sharp_use_bweight:
                        if e[bw] == 0:
                            e[bw] = 1
        else:
            if any(e[bw] == 1 for e in selected):
                for e in selected:
                    if self.dont_affect_bevel:
                        if get_preferences().property.sharp_use_bweight:
                            if e[bw] == 1:
                                e[bw] = 0
                        if get_preferences().property.sharp_use_crease:
                            e[cr] = 0
                        if get_preferences().property.sharp_use_sharp:
                            e.smooth = True
                        if get_preferences().property.sharp_use_seam:
                            e.seam = False

                    else:
                        if get_preferences().property.sharp_use_bweight:
                            e[bw] = 0
                        if get_preferences().property.sharp_use_crease:
                            e[cr] = 0
                        if get_preferences().property.sharp_use_sharp:
                            e.smooth = True
                        if get_preferences().property.sharp_use_seam:
                            e.seam = False
            else:
                for e in selected:
                    if self.dont_affect_bevel:
                        if get_preferences().property.sharp_use_bweight:
                            if e[bw] == 0:
                                e[bw] = 1
                            else:
                                e[bw] = 0
                        if get_preferences().property.sharp_use_crease:
                            if e[cr] == 1:
                                e[cr] = 0
                            else:
                                e[cr] = 1
                        if get_preferences().property.sharp_use_sharp:
                            e.smooth = not e.smooth
                        if get_preferences().property.sharp_use_seam:
                            e.seam = not e.seam
                    else:
                        if get_preferences().property.sharp_use_bweight:
                            e[bw] = 1
                        if get_preferences().property.sharp_use_crease:
                            if e[cr] == 1:
                                e[cr] = 0
                            else:
                                e[cr] = 1
                        if get_preferences().property.sharp_use_sharp:
                            e.smooth = not e.smooth
                        if get_preferences().property.sharp_use_seam:
                            e.seam = not e.seam

        bmesh.update_edit_mesh(me)

        return {'FINISHED'}


    def sync_apply_seam(self, me, edges):
        '''Sync the seams instead of toggle.'''

        if not get_preferences().property.sharp_use_bweight:
            if not get_preferences().property.sharp_use_crease:
                if not get_preferences().property.sharp_use_sharp:
                    if get_preferences().property.sharp_use_seam:

                        mark_seams = True
                        if any(e for e in edges if e.seam):
                            mark_seams = False

                        if mark_seams:
                            for e in edges:
                                e.seam = True
                        else:
                            for e in edges:
                                e.seam = False
                        bmesh.update_edit_mesh(me)
                        return True
        return False


    def sync_apply_crease(self, me, cr, edges):
        '''Sync the seams instead of toggle.'''

        if not get_preferences().property.sharp_use_bweight:
            if not get_preferences().property.sharp_use_seam:
                if not get_preferences().property.sharp_use_sharp:
                    if get_preferences().property.sharp_use_crease:

                        mark_crease = True
                        if any(e for e in edges if e[cr] == 1):
                            mark_crease = False

                        if mark_crease:
                            for e in edges:
                                e[cr] = 1
                        else:
                            for e in edges:
                                e[cr] = 0
                        bmesh.update_edit_mesh(me)
                        return True
        return False


    def sync_apply_sharps(self, me, edges):
        '''Sync the seams instead of toggle.'''

        if not get_preferences().property.sharp_use_bweight:
            if not get_preferences().property.sharp_use_seam:
                if not get_preferences().property.sharp_use_crease:
                    if get_preferences().property.sharp_use_sharp:

                        mark_sharp = True
                        if any(e for e in edges if e.smooth == False):
                            mark_sharp = False

                        if mark_sharp:
                            for e in edges:
                                e.smooth = False
                        else:
                            for e in edges:
                                e.smooth = True
                                
                        bmesh.update_edit_mesh(me)
                        return True
        return False