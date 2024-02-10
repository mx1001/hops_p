import bpy

from bpy.types import PropertyGroup
from bpy.props import BoolProperty, EnumProperty


def active_obj_mirror_mods(scene, context):

    modifiers = []
    obj = context.active_object
    if obj.type == "GPENCIL":
        mods = [mod for mod in obj.grease_pencil_modifiers if mod.type == "GP_MIRROR"]
    else:
        mods = [mod for mod in obj.modifiers if mod.type == "MIRROR"]
    for mod in mods:
        modifiers.append((f"{mod.name}", f"{mod.name}", ""))
    if len(mods) == 0:
        modifiers.append(("new", "New", ""))
    return modifiers


class props(PropertyGroup):

    running: BoolProperty(
        name='Mirror is Running',
        description='Mirror modal operation is running',
        default=False)

    advanced: BoolProperty(
        name='Mirror Advanced options',
        description='''Advanced / Simple Toggle

        Mirror Advanced options display

        Shortcut: Tab 
        ''',
        default=False)

    modifier: EnumProperty(
        name="Mirror Modifiers",
        description="Mirror modifier to be affected",
        items=active_obj_mirror_mods)

    mode: EnumProperty(
        name="Mirror Mode",
        description="Mirror selected objects mode",
        items=[("MODIFIER", "Modifier", "Modify last mirror modifier options"),
               ("NEWMODIFIER", "New Modifier", "Create new mirror modifier"),
               ("MODIFIERAPPLY", "Modifier&Apply", "Apply mirror modifier (symmetrize)"),
               ("BISECTMOD", "Bisect&Modifier", "Bisect the mesh and add mirror modifier"),
               ("BISECT", "Bisect", "Bisect the mesh"),
               ("SYMMETRY", "Symmetry", "Use symetrize operator")],
        default='MODIFIER')

    orientation: EnumProperty(
        name="Mirror Orientation",
        description="Mirror selected objects using orientation",
        items=[("LOCAL", "Local", "Local Orientation", "ORIENTATION_LOCAL", 1),
               ("GLOBAL", "Global", "Global Orientation", "ORIENTATION_GLOBAL", 2),
               ("VIEW", "View", "View Orientation", "ORIENTATION_VIEW", 3),
               ("CURSOR", "Cursor", "Cursor Orientation", "ORIENTATION_CURSOR", 4)],
        default='LOCAL')

    pivot: EnumProperty(
        name="Mirror Pivot Point",
        description="Mirror selected objects across pivot point",
        items=[("ACTIVE", "Active Origin", "", "PIVOT_ACTIVE", 1),
               ("MEDIAN", "Median Point", "", "PIVOT_MEDIAN", 2),
               ("CURSOR", "Cursor", "", "PIVOT_CURSOR", 3),
               ("INDIVIDUAL", "Individual Origins", "", "PIVOT_INDIVIDUAL", 4)],
        default='ACTIVE')

    include_active: BoolProperty(
        name='Include Active',
        description='Include Active Object in Group Mirroring',
        default=False)

    close: BoolProperty(
        name='Close After Operation',
        description='Close when first mirror operation is done using gizmo',
        default=True)

    parent_empty: BoolProperty(
        name='Parent Empty',
        description='Parent empty to active object',
        default=False)

    revert: BoolProperty(
        name='Revert Gizmo Handlers',
        description='Reverting gizmo manipulator handlers',
        default=False)

    mirror_u: BoolProperty(
        name='Modifier mirror_u property',
        description='Set mirror_u on modifier',
        default=False)

    mirror_v: BoolProperty(
        name='Modifier mirror_v property',
        description='Set mirror_v on modifier',
        default=False)
