

def hide_preview(context, obj):

    if hasattr(obj, 'cycles_visibility'):
        obj.cycles_visibility.camera = False
        obj.cycles_visibility.diffuse = False
        obj.cycles_visibility.glossy = False
        obj.cycles_visibility.shadow = False
        obj.cycles_visibility.scatter = False
        obj.cycles_visibility.transmission = False


def show_preview(context, obj):

    if hasattr(obj, 'cycles_visibility'):
        obj.cycles_visibility.camera = True
        obj.cycles_visibility.diffuse = True
        obj.cycles_visibility.glossy = True
        obj.cycles_visibility.shadow = True
        obj.cycles_visibility.scatter = True
        obj.cycles_visibility.transmission = True
