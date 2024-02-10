
'''
Capture event data.
Check event data on all the windows and cells.
Respond to events.
Update prefs.
'''


class Event_System():

    def __init__(self, db):

        # DB
        self.db = db


    def update_event_data(self, event, context):
        '''Capture all the event data from the modal.'''

        self.db.event.update_events(event=event, context=context)


    def run(self):
        '''Runs the main event loop on the UI'''

        self.toggle_windows_check()
        self.setup_dims()
        self.event()


    def toggle_windows_check(self):

        if self.db.event.h_key_pressed:
            self.db.prefs.ui.Hops_modal_help_visible = not self.db.prefs.ui.Hops_modal_help_visible

        if self.db.event.m_key_pressed:
            self.db.prefs.ui.Hops_modal_mods_visible = not self.db.prefs.ui.Hops_modal_mods_visible


    def setup_dims(self):
        '''Setup all the dimensions.'''

        for key, val in self.db.windows.items():

            if val.window_key == "Help":
                val.visible = self.db.prefs.ui.Hops_modal_help_visible

            elif val.window_key == "Mods":
                val.visible = self.db.prefs.ui.Hops_modal_mods_visible

            if val.visible:
                val.setup()


    def event(self):
        '''Run the events.'''

        # Mouse checks for the window
        for key, val in self.db.windows.items():
            if val.visible:
                val.event_check()
            # Make sure the DB does not contain a ref to an inactive window (window is not visible)
            else:
                if key == self.db.ui_event.active_window_key:
                    self.db.ui_event.active_window_key = ""

        # If the mouse check found a window run its event
        for key, val in self.db.windows.items():
            if val.visible:
                if key == self.db.ui_event.active_window_key:
                    val.run_event()

        # Check to see if any of the windows are active (The window is transforming)
        reset = True
        for key, val in self.db.windows.items():
            if val.active:
                reset = False

        # Free up the active window slots for another window to become active
        if reset:
            if not self.db.event.mouse_dragging:
                self.db.ui_event.active_window_key = ""

        # Free up the cell lock
        if self.db.event.left_click_released:
            self.db.ui_event.cell_blocking = False
            self.db.ui_event.cell_index = None