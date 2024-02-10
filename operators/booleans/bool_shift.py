import bpy
from ... utils.objects import set_active
from ... material import assign_material
from ... preferences import get_preferences
from ... utility import collections, modifier
from ... utility.renderer import cycles
from ... ui_framework.master import Master
from ... ui_framework.operator_ui import Master as InstantMaster
from ... utils.toggle_view3d_panels import collapse_3D_view_panels
from ...utility.base_modal_controls import Base_Modal_Controls

class HOPS_OT_BoolShift(bpy.types.Operator):
    bl_idname = "hops.bool_shift"
    bl_label = "Hops Shift Boolean"
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING'}
    bl_description = """Bool Shift
LMB - Change an existing boolean relationship
Shift + LMB - Perform the shift operation you probably want and finish instantly
Ctrl + LMB - Keep bevel modifiers on inset objects if they don't use vertex groups or bevel weight"""


    operation: bpy.props.EnumProperty(
        name="Operation",
        description="What kind of boolean operation to change to",
        items=[
            ('INTERSECT', "Intersect", "Peform an intersect operation"),
            ('UNION', "Union", "Peform a union operation"),
            ('DIFFERENCE', "Difference", "Peform a difference operation"),
            ('SLASH', "Slash", "Peform a slash operation"),
            ('INSET', "Inset", "Peform an inset operation"),
            ('OUTSET', "Outset", "Peform an outset operation"),
            ('CLEAR', "Clear", "Clear the boolean relationship")],
        default='DIFFERENCE')


    thickness: bpy.props.FloatProperty(
        name="Thickness",
        description="How deep the inset should cut",
        default=0.10,
        min=0.00,
        # soft_max=10.0,
        # step=1,
        precision=3)


    keep_bevels: bpy.props.BoolProperty(
        name="Keep Bevels",
        description="Keep Bevel modifiers on inset objects enabled if they don't use vertex groups or bevel weight",
        default=False)


    @classmethod
    def poll(cls, context):

        # Just make sure we're in object mode
        return context.mode == 'OBJECT'


    def draw(self, context):

        # Always draw the boolean operation
        self.layout.prop(self, "operation")

        # Thickness and Keep Bevels are only relevant to inset and outset
        if self.operation in ('INSET', 'OUTSET'):
            self.layout.prop(self, "thickness")
            self.layout.prop(self, "keep_bevels")


    def invoke(self, context, event):

        # Shift Click performs Instant Shift
        if event.type == 'LEFTMOUSE' and event.shift:
            return self.instant_slash(context, event)

        self.thick_adjust = False
        # It is necessary to push an undo step here to prevent issues
        bpy.ops.ed.undo_push()

        # Keep this consistent with bool_inset
        self.keep_bevels = event.ctrl

        # Find the likely desired operation
        booleans = self.find_booleans(context)
        cutters = self.find_cutters(context)
        slashes = self.find_slashes(booleans, cutters)
        self.operation = self.initial_operation(booleans, cutters, slashes)

        # Let the user know what we're doing, then do it
        self.report_info(self.operation)
        self.execute(context)

        # UI System
        self.master = Master(context=context)
        self.master.only_use_fast_ui = True
        #self.timer = context.window_manager.event_timer_add(0.025, window=context.window)

        self.original_tool_shelf, self.original_n_panel = collapse_3D_view_panels()
        context.window_manager.modal_handler_add(self)
        self.base_controls = Base_Modal_Controls(context, event)
        return {'RUNNING_MODAL'}


    def modal(self, context, event):

        # UI
        self.master.receive_event(event=event)
        self.base_controls.update(context, event)
        # Pass through anything involving middle mouse click, so people can still move their view
        if self.base_controls.pass_through:
            return {'PASS_THROUGH'}

        # Pass through Shift + Z and Alt + Z for xray shortcuts
        elif event.type == 'Z' and (event.shift or event.alt):
            return {'PASS_THROUGH'}

        # Left Click or Space confirm
        elif self.base_controls.confirm:
            self.report_info('FINISHED')
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            return {'FINISHED'}

        # Right Click or Esc cancel
        elif self.base_controls.cancel:
            self.report_info('CANCELLED')
            self.cancel(context)
            collapse_3D_view_panels(self.original_tool_shelf, self.original_n_panel)
            self.master.run_fade()
            return {'CANCELLED'}

        # You can use mouse scroll or X and Z to scroll through boolean operations
        elif self.base_controls.scroll or (event.type in {'X', 'Z'} and event.value == 'PRESS'):
            if event.type == 'X':
                self.scroll(1)
            elif event.type == 'Z':
                self.scroll(-1)
            else:
                self.scroll(self.base_controls.scroll)

            # Let the user know what we're doing, then do it
            self.report_info(self.operation)
            self.cancel(context)
            self.execute(context)

        elif event.type == 'T' and event.value == 'PRESS' :
            self.thick_adjust = not self.thick_adjust

        elif self.base_controls.mouse and self.thick_adjust and self.operation in {'INSET', 'OUTSET'}:
            self.thickness +=self.base_controls.mouse
            self.cancel(context)
            self.execute(context)

        # H opens the help
        if event.type == 'H' and event.value == 'PRESS':
            get_preferences().property.hops_modal_help = not get_preferences().property.hops_modal_help
            context.area.tag_redraw()

        # UI
        self.draw_modal(context)

        # Continue running the modal
        return {'RUNNING_MODAL'}


    def execute(self, context):

        # Get the booleans, cutters, and slashes
        booleans = self.find_booleans(context)
        cutters = self.find_cutters(context)
        slashes = self.find_slashes(booleans, cutters)

        # List of objects we've removed
        removed = []

        # Iterate through boolean modifiers using chosen cutters
        for cutter in cutters:

            # These are the targets of this cutter
            for target_one, modifier_one in booleans[cutter]:

                # If this target has been removed, skip it
                if target_one in removed:
                    continue

                # Only do these operations if the target is not an inset object
                if not (target_one.hops.status == 'BOOLSHAPE' and modifier_one == target_one.modifiers[-1]):

                    # Handle difference to slash
                    if self.operation == 'SLASH':

                        # Make sure we're not making duplicate slashes
                        if not slashes[cutter]:
                            slash = self.slash(context, target_one, modifier_one, cutter)
                            slashes[cutter].append(slash)

                    # Handle slash to other
                    elif target_one in slashes[cutter]:

                        # Delete the existing slash object
                        bpy.data.objects.remove(target_one, do_unlink=True)

                        # And add it to the removed list
                        removed.append(target_one)

                        # Skip the rest of this loop because the target no longer exists
                        continue

                    # Handle difference to inset
                    if self.operation in ('INSET', 'OUTSET'):
                        self.inset(context, target_one, modifier_one, cutter, None)

                    # Handle difference to difference
                    if self.operation in ('DIFFERENCE', 'UNION', 'INTERSECT'):
                        self.difference(context, target_one, modifier_one, cutter)

                    # Handle difference to none
                    if self.operation == 'CLEAR':
                        self.clear(context, target_one, modifier_one, cutter)

                # Only do this for loop if we're sure that the target is an inset object
                else:

                    # These are the targets of this inset
                    for target_two, modifier_two in booleans[target_one]:

                        # Only do these operations if the target is not an inset object
                        if not (target_two.hops.status == 'BOOLSHAPE' and modifier_two == target_two.modifiers[-1]):

                            # Handle inset to slash
                            if self.operation == 'SLASH':

                                # Make sure we're not making duplicate slashes
                                if not slashes[cutter]:
                                    slash = self.slash(context, target_two, modifier_two, cutter)
                                    slashes[cutter].append(slash)

                            # Make sure the inset object still exists
                            if target_one not in removed:

                                # Handle inset to inset
                                if self.operation in ('INSET', 'OUTSET'):
                                    self.inset(context, target_two, modifier_two, cutter, target_one)

                                # Handle inset to other
                                else:

                                    # Delete the existing inset object
                                    bpy.data.objects.remove(target_one, do_unlink=True)

                                    # And add it to the removed list
                                    removed.append(target_one)

                            # Handle inset to difference
                            if self.operation in ('DIFFERENCE', 'UNION', 'INTERSECT'):
                                self.difference(context, target_two, modifier_two, cutter)

                            # Handle difference to none
                            if self.operation == 'CLEAR':
                                self.clear(context, target_two, modifier_two, cutter)

        # Success!
        return {'FINISHED'}


    def cancel(self, context):
        bpy.ops.ed.undo_push()
        bpy.ops.ed.undo()


    def instant_slash(self, context, event):

        # Keep this consistent with bool_inset
        self.keep_bevels = event.ctrl

        # Find the likely desired operation
        booleans = self.find_booleans(context)
        cutters = self.find_cutters(context)
        slashes = self.find_slashes(booleans, cutters)
        self.operation = self.initial_operation(booleans, cutters, slashes)

        # Let the user know what we're doing, then do it
        self.report_info(self.operation)
        self.execute(context)

        instant_master = InstantMaster()

        draw_data = [
            ["Instant Shift"],
            ["Operation", self.operation.capitalize()],
        ]

        instant_master.receive_draw_data(draw_data=draw_data)
        instant_master.draw()

        return {'FINISHED'}


    def report_info(self, info):
        words = [w.capitalize() for w in str(info).split("_")]
        self.report({'INFO'}, " ".join(words))


    def scroll(self, direction):
        operations = ('INTERSECT', 'UNION', 'DIFFERENCE', 'SLASH', 'INSET', 'OUTSET', 'CLEAR')
        index = (operations.index(self.operation) + direction) % len(operations)
        self.operation = operations[index]


    def find_booleans(self, context):

        # Lookup table to find booleans using a cutter
        booleans = {o:[] for o in context.blend_data.objects}
        for obj in context.blend_data.objects:

            # Only add objects that are linked to a collection
            if obj.users_collection:
                for mod in obj.modifiers:

                    # Only add boolean modifiers that have a cutter
                    if mod.type == 'BOOLEAN' and mod.object:

                        # Only add insets and visible targets
                        if obj.hops.status == 'BOOLSHAPE' or obj.visible_get():
                            booleans[mod.object].append((obj, mod))

        return booleans


    def find_cutters(self, context):

        # List of cutters to iterate through
        cutters = []
        for obj in context.selected_objects:

            # If this object is not a mesh, skip it
            if obj.type != 'MESH':
                continue

            # If this object is not a boolshape, skip it
            if obj.hops.status != 'BOOLSHAPE':
                continue

            # Get the last modifier on this cutter
            mod = obj.modifiers[-1] if obj.modifiers else None

            # If this cutter is an inset, add its intersect cutter to the list instead
            if mod and mod.type == 'BOOLEAN' and mod.operation == 'INTERSECT':
                if mod.object and mod.object.users_collection:
                    cutters.append(mod.object)

            # Otherwise it's not an inset, so just add it to the list
            elif obj.users_collection:
                cutters.append(obj)

        # Filter out any duplicate items just in case
        cutters = list(dict.fromkeys(cutters))

        return cutters


    def find_slashes(self, booleans, cutters):

        # Lookup tables for finding difference and intersect targets of a cutter
        dif_bools = {o:[] for o in cutters}
        int_bools = {o:[] for o in cutters}
        for cutter in cutters:
            for target, modifier in booleans[cutter]:

                # We care about slashes, not insets
                if target.hops.status != 'BOOLSHAPE':
                    if modifier.operation == 'DIFFERENCE':
                        dif_bools[cutter].append(target)
                    elif modifier.operation == 'INTERSECT':
                        int_bools[cutter].append(target)

        # Lookup table for finding slashes of a cutter
        slashes = {o:[] for o in cutters}
        for cutter in cutters:

            # If this cutter has any difference targets
            if dif_bools[cutter]:

                # Then assume any intersect targets are slashes
                for target in int_bools[cutter]:
                    slashes[cutter].append(target)

        return slashes


    def initial_operation(self, booleans, cutters, slashes):

        # Base the initial operation on the first boolean we find
        for cutter in cutters:
            for target_one, modifier_one in booleans[cutter]:

                # We're not dealing with inset
                if not (target_one.hops.status == 'BOOLSHAPE' and modifier_one == target_one.modifiers[-1]):

                    # If we're dealing with slash, shift to difference
                    if slashes[cutter]:
                        return 'DIFFERENCE'

                    # If we're dealing with difference, shift to slash
                    elif modifier_one.operation == 'DIFFERENCE':
                        return 'SLASH'

                    # If we're dealing with union or intersect, shift to difference
                    elif modifier_one.operation in ('UNION', 'INTERSECT'):
                        return 'DIFFERENCE'

                # We're dealing with inset
                for target_two, modifier_two in booleans[target_one]:

                    # If we're dealing with outset, shift to inset
                    if modifier_two.operation == 'DIFFERENCE':
                        return 'OUTSET'

                    # If we're dealing with inset, shift to outset
                    elif modifier_two.operation == 'UNION':
                        return 'INSET'

        # If for some reason we can't find anything, shift to clear
        return 'CLEAR'


    def difference(self, context, target, modifier, cutter):

        # Set the boolean modifier to the desired operation
        modifier.operation = self.operation

        # For inset to difference it's important we make sure to set the object
        modifier.object = cutter


    def slash(self, context, target, modifier, cutter):

        # The newly created object
        slash = None

        # There's no point creating slash objects of boolshapes
        if target.hops.status != 'BOOLSHAPE':

            # First create the slash object
            slash = target.copy()
            slash.data = target.data.copy()
            target.users_collection[0].objects.link(slash)

            # Then iterate through its modifiers
            start_deleting = False
            for mod in slash.modifiers:

                # Check whether this modifier is the one we're replacing on the target
                if mod.type == 'BOOLEAN' and mod.object == modifier.object:

                    # And set it to intersect
                    mod.operation = 'INTERSECT'

                    # For inset to slash it's important we make sure to set the object
                    mod.object = cutter

                    # Then start deleting modifiers
                    start_deleting = True

                # Which come after this one
                elif mod.type == 'BOOLEAN' and start_deleting:
                    slash.modifiers.remove(mod)

        # Set the original modifier to difference
        modifier.operation = 'DIFFERENCE'

        # For inset to slash it's important we make sure to set the object
        modifier.object = cutter

        # Return the new object
        return slash


    def inset(self, context, target, modifier, cutter, inset):

        # Modify the existing inset if there is one
        if inset:

            # Iterate through the modifiers backwards to get the last solidify
            for mod in [m for m in inset.modifiers][::-1]:
                if mod.type == 'SOLIDIFY':
                    mod.thickness = self.thickness
                    break

        # Otherwise create a new inset object
        else:
            inset = target.copy()
            inset.data = target.data.copy()
            collections.link_obj(context, inset, "Cutters")
            cycles.hide_preview(context, inset)
            inset.hops.status = 'BOOLSHAPE'
            inset.display_type = 'WIRE'
            inset.hide_render = True

            # Iterate through its modifiers
            start_deleting = False
            for mod in inset.modifiers:

                # Check whether this modifier is the one we're replacing on the target
                if mod.type == 'BOOLEAN' and mod.object == modifier.object:

                    # Then start deleting modifiers
                    start_deleting = True

                # Including this one and all that come after it
                if start_deleting:
                    inset.modifiers.remove(mod)

            # First create a solidify modifier on the inset
            solidify = inset.modifiers.new(name="Solidify", type='SOLIDIFY')
            solidify.use_even_offset = True
            solidify.thickness = self.thickness
            solidify.offset = 0.0
            solidify.show_expanded = True

            # Then create a boolean intersect modifier on the inset
            intersect = inset.modifiers.new(name="Boolean", type='BOOLEAN')
            intersect.operation = 'INTERSECT'
            intersect.object = cutter

        # Handle existing bevel modifiers
        for mod in inset.modifiers:
            if mod.type == 'BEVEL' and not self.keep_bevels:
                if mod.limit_method not in ('VGROUP', 'WEIGHT'):
                    mod.show_render = mod.show_viewport = False
            elif mod.type == 'WEIGHTED_NORMAL':
                inset.modifiers.remove(mod)

        # Set the original modifier to the desired operation
        modifier.operation = 'DIFFERENCE' if self.operation == 'INSET' else 'UNION'

        # And change the original modifier's object to the newly created inset
        modifier.object = inset


    def clear(self, context, target, modifier, cutter):

        # Simply remove the boolean modifier
        target.modifiers.remove(modifier)


    def draw_modal(self, context):

        # Make the operation text look nice
        operation = str(self.operation).capitalize()

        # Start
        self.master.setup()

        ########################
        #   Fast UI
        ########################

        if self.master.should_build_fast_ui():

            win_list = []
            help_list = []

            # Main
            if get_preferences().ui.Hops_modal_fast_ui_loc_options != 1:
                win_list.append(operation)
                if self.operation in ('INSET', 'OUTSET'):
                    win_list.append(f"{self.thickness:.2f}")
            else:
                win_list.append("Shift Boolean")
                win_list.append(f"Mode : {operation}")
                if self.operation in ('INSET', 'OUTSET'):
                    win_list.append(f"Thickness : {self.thickness:.3f}")
                    if context.active_object.mode == 'OBJECT':
                        win_list.append(f"Keep Bevels : {self.keep_bevels}")

            # Help
            help_list.append(["T",  "Thickness Adjust"])
            help_list.append(["Wheel",  "Switch Operation"])
            help_list.append(["X / Z",  "Switch Operation"])
            help_list.append(["H",      "Toggle help"])
            help_list.append(["~",      "Toggle viewport displays."])

            self.master.receive_fast_ui(win_list=win_list, help_list=help_list, image="ShiftBool")

        # Finished
        self.master.finished()
