import bpy
from .. utils.addons import addon_exists

used_addons = [
    ('kitops',              'Kit_OPS' or 'kitops',             'https://gumroad.com/l/kitopsprolite/'),
    ('Cablerator',          'Cablerator',                      'https://gumroad.com/l/cblrtr/operative'),
    ('Powersave',           'PowerSave' or 'Powersave',        'https://gumroad.com/l/powersave'),
    ('Boxcutter',           'Boxcutter',                       'https://gumroad.com/l/BoxCutter/iamanoperative'),
    ('mira_tools',          'Mira Tools',                      'https://blenderartists.org/t/miratools/637385'),
    ('MESHmachine',         'MESHmachine',                     'https://gumroad.com/l/MESHmachine/decalarmy')
]

recommended_addons = [
    ("GroupPro",            "Group Pro",        "https://gumroad.com/l/GroupPro/for_operatives#"),
    ('mesh_shaper',         'Mesh Shaper',      'https://gumroad.com/l/bezier_mesh_shaper'),
    ("power_snapping_pies", "Snapping Pies",    "https://github.com/mx1001/power_snapping_pies"),
    ("DECALmachine",        "DECALmachine",     "https://gumroad.com/l/DECALmachine/"),
    ('batch_ops',           'Batch_OPS',        'https://gum.co/batchops'),
    ('zen_uv',           'Zen UV',              'https://gumroad.com/l/ZenUV/HOPscutter'),
]

def draw_addon_diagnostics(layout, columns = 4):
    col = layout.column()
    col.label(text="Recommended Addons:")
    draw_addon_table(col, used_addons, columns, True)

    col = layout.column()
    col.label(text="Additional Addons:")
    draw_addon_table(col, recommended_addons, columns, False)

def draw_addon_table(layout, addons, columns, show_existance):
    col = layout.column()
    for i, (identifier, name, url) in enumerate(addons):
        if i % columns == 0: row = col.row()
        icon = addon_icon(identifier, show_existance)
        row.operator("wm.url_open", text=name, icon = icon).url = url

    if len(addons) % columns != 0:
        for i in range(0, columns - len(addons) % columns):
            row.label(text="")

def addon_icon(addon_identifier, show_existance):
    if show_existance:
        if addon_exists(addon_identifier): return "FILE_TICK"
        else: return "ERROR"
    else:
        return "NONE"
