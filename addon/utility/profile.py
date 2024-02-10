import bpy
import pathlib
import json


def get_bevel_profile(mod: bpy.types.BevelModifier) -> dict:
    profile = mod.custom_profile
    points = profile.points

    data = {
        'segments': mod.segments,
        'profile': {
            'use_sample_straight_edges':  profile.use_sample_straight_edges,
            'use_sample_even_lengths': profile.use_sample_even_lengths,
            'points': [],
        },
    }

    for point in points:
        data['profile']['points'].append({
            'handle_type_1': point.handle_type_1,
            'handle_type_2': point.handle_type_2,
            'location': point.location[:],
        })

    return data


def save_bevel_profile(mod: bpy.types.BevelModifier, path: str) -> tuple:
    if getattr(mod, 'use_custom_profile', True) == False:
        return {'WARNING'}, f'Modifier "{mod.name}" is not using a custom profile', {'CANCELLED'}
    elif getattr(mod, 'profile_type', 'CUSTOM') != 'CUSTOM':
        return {'WARNING'}, f'Modifier "{mod.name}" is not using a custom profile', {'CANCELLED'}

    data = get_bevel_profile(mod)
    data = json.dumps(data, indent=4)

    path = bpy.path.abspath(path)
    path = pathlib.Path(path).resolve()

    try:
        size = path.write_text(data)
    except:
        size = None

    if size:
        return {'INFO'}, f'Saved "{path.name}"', {'FINISHED'}
    else:
        return {'ERROR'}, f'Failed to save "{path.name}"', {'CANCELLED'}


def set_bevel_profile(mod: bpy.types.BevelModifier, data: dict, sync_segments: bool) -> bool:
    if hasattr(mod, 'use_custom_profile'):
        mod.use_custom_profile = True
    elif hasattr(mod, 'profile_type'):
        mod.profile_type = 'CUSTOM'

    profile = mod.custom_profile
    points = profile.points

    mod.segments = len(data['profile']['points']) if sync_segments else data['segments']
    profile.use_sample_straight_edges = data['profile']['use_sample_straight_edges']
    profile.use_sample_even_lengths = data['profile']['use_sample_even_lengths']

    handle_type_1 = points[0].bl_rna.properties['handle_type_1']
    handle_types = [v.identifier for v in handle_type_1.enum_items]

    while len(points) > 2:
        points.remove(points[1])

    points[0].location = (0.0, 0.5)
    points[-1].location = (1.0, 0.5)
    total = len(data['profile']['points']) - 1

    for index, point_data in enumerate(data['profile']['points'][1:-1], start=1):
        point = points.add(index / total, 0.5)

        handle_type_1 = point_data['handle_type_1']
        if handle_type_1 in handle_types:
            point.handle_type_1 = handle_type_1
        else:
            print(f'{handle_type_1} is not supported')
            point.handle_type_1 = 'AUTO'

        handle_type_2 = point_data['handle_type_2']
        if handle_type_2 in handle_types:
            point.handle_type_2 = handle_type_2
        else:
            print(f'{handle_type_2} is not supported')
            point.handle_type_2 = 'AUTO'

    for index, point_data in enumerate(data['profile']['points']):
        location = point_data['location']
        points[index].location = location

    profile.update()
    return True


def load_bevel_profile(mod: bpy.types.BevelModifier, path: str, sync_segments: bool) -> tuple:
    path = bpy.path.abspath(path)
    path = pathlib.Path(path).resolve()

    try:
        data = path.read_text()
    except:
        data = None

    if data:
        data = json.loads(data)
    else:
        return {'ERROR'}, f'Failed to load "{path.name}"', {'CANCELLED'}

    if set_bevel_profile(mod, data, sync_segments):
        return {'INFO'}, f'Loaded "{path.name}"', {'FINISHED'}
