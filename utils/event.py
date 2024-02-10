

class Event_Clone:

    def __init__(self, event):

        self.can_update = True
        self.update_count = 0

        # Alternations
        self.alt = event.alt
        self.ascii = event.ascii
        self.ctrl = event.ctrl
        self.is_mouse_absolute = event.is_mouse_absolute
        self.is_tablet = event.is_tablet
        self.mouse_prev_x = event.mouse_prev_x
        self.mouse_prev_y = event.mouse_prev_y
        self.mouse_region_x = event.mouse_region_x
        self.mouse_region_y = event.mouse_region_y
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        self.oskey = event.oskey
        self.pressure = event.pressure
        self.shift = event.shift
        self.tilt = event.tilt

        # Key
        self.type = event.type

        # Press
        self.value = event.value

    
    def alter_event(self, new_type="", new_value="", alternations=[]):

        self.can_update = False

        # Key
        self.type = new_type

        # Press
        self.value = new_value

        # Adjust the alternation keys
        for alter in alternations:
            for item in dir(self):
                if item == alter[0]:
                    setattr(self, str(item), alter[1])


    def update(self, event):


        if self.can_update:

            # Alternative
            self.alt = event.alt
            self.ascii = event.ascii
            self.ctrl = event.ctrl
            self.is_mouse_absolute = event.is_mouse_absolute
            self.is_tablet = event.is_tablet
            self.mouse_prev_x = event.mouse_prev_x
            self.mouse_prev_y = event.mouse_prev_y
            self.mouse_region_x = event.mouse_region_x
            self.mouse_region_y = event.mouse_region_y
            self.mouse_x = event.mouse_x
            self.mouse_y = event.mouse_y
            self.oskey = event.oskey
            self.pressure = event.pressure
            self.shift = event.shift
            self.tilt = event.tilt
            # Key
            self.type = event.type
            # Press
            self.value = event.value
    
        else:
            self.can_update = True