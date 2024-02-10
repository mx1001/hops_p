

def add_list_items(create=None, layout=None, dict_val=[], color_select=0, target_size=12, scrollable=False):
    '''Take complicated list items and break them down into the elements.'''

    drag = True if dict_val[-1] == True else False

    if type(dict_val) == str:
        create.element_border(layout=layout, line_width=1)
        create.element_text(layout=layout, text=dict_val, color_select=color_select, target_size=target_size)

    if len(dict_val) > 0:

        if len(dict_val) == 1:
            create.element_border(layout=layout, line_width=1)
            create.element_text(layout=layout, text=dict_val[0], color_select=color_select, target_size=target_size)

        elif len(dict_val) == 2:
            if drag:
                create.event_call_drag(layout=layout, func=dict_val[1])
            else:
                create.event_call_back(layout=layout, func=dict_val[1], scrollable=scrollable)

            create.element_border(layout=layout, line_width=1)
            create.element_text(layout=layout, text=dict_val[0], color_select=color_select, target_size=target_size)

        elif len(dict_val) == 3:
            if drag:
                create.event_call_drag(layout=layout, func=dict_val[1], positive_args=dict_val[2])
            
            else:
                create.event_call_back(layout=layout, func=dict_val[1], positive_args=dict_val[2], scrollable=scrollable)

            create.element_border(layout=layout, line_width=1)
            create.element_text(layout=layout, text=dict_val[0], color_select=color_select, target_size=target_size)

        elif len(dict_val) == 4:
            if drag:
                create.event_call_drag(layout=layout, func=dict_val[1], positive_args=dict_val[2], negative_args=dict_val[3])
            
            else:
                create.event_call_back(layout=layout, func=dict_val[1], positive_args=dict_val[2], negative_args=dict_val[3], scrollable=scrollable)

            create.element_border(layout=layout, line_width=1)
            create.element_text(layout=layout, text=dict_val[0], color_select=color_select, target_size=target_size)

        elif len(dict_val) == 5:
            if drag:
                create.event_call_drag(layout=layout, func=dict_val[1], positive_args=dict_val[2], negative_args=dict_val[3])
            
            else:
                create.event_call_back(layout=layout, func=dict_val[1], positive_args=dict_val[2], negative_args=dict_val[3], scrollable=scrollable)

            create.element_border(layout=layout, line_width=1)
            create.element_text(layout=layout, text=dict_val[0], color_select=color_select, target_size=target_size)


def toggle_help(db=None):
    '''Toggle the help window.'''

    db.prefs.ui.Hops_modal_help_visible = not db.prefs.ui.Hops_modal_help_visible


def toggle_mods(db=None):
    '''Toggle the mods window.'''

    db.prefs.ui.Hops_modal_mods_visible = not db.prefs.ui.Hops_modal_mods_visible
