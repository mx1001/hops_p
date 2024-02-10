import time

class Drag_Event():

    time_diff = 0
    start_time = None
    wait_time_from_first_click = .25

    def __init__(self):

        self.db = None
        self.func = None
        self.positive_args = None
        self.negative_args = None
        self.cell_index = None
        self.cell_center_x = None
 
    
    def __del__(self):

        # Event will turn the cell_index to none on left click release
        if self.db.ui_event.cell_index == None:
            Drag_Event.time_diff = 0
            Drag_Event.start_time = None


    def event(self):

        if self.func != None:

            can_call = False

            if Drag_Event.start_time == None:
                Drag_Event.start_time = time.time()

            if time.time() - Drag_Event.start_time > Drag_Event.wait_time_from_first_click:

                # Fine tune
                if self.db.event.shift_pressed:

                    if Drag_Event.time_diff != round(time.time() - Drag_Event.start_time, 2):
                        can_call = True
                        Drag_Event.time_diff = round(time.time() - Drag_Event.start_time, 2)

                else:
                    if Drag_Event.time_diff != round(time.time() - Drag_Event.start_time, 1):
                        can_call = True
                        Drag_Event.time_diff = round(time.time() - Drag_Event.start_time, 1)

                # Keep calling while dragging
                if can_call:
                    if self.cell_center_x != None:
                        self.call_func()


    def set_hook(self):

        self.db.ui_event.cell_index = self.cell_index

        if Drag_Event.start_time == None:
            Drag_Event.start_time = time.time()

        self.call_func()
        

    def call_func(self):

        try:
            # Mouse is on left side
            if self.db.event.mouse_pos[0] < self.cell_center_x:
                if self.negative_args != None:
                    self.func(*self.negative_args)

            # Mouse is on right side
            elif self.db.event.mouse_pos[0] > self.cell_center_x:
                if self.positive_args != None:
                    self.func(*self.positive_args)
        
        except:
            pass


    def external_cell_event_call(self, positive=True):
        '''Used for scrolling, the cells event will call this not self.'''

        if self.func != None:

            if positive == True:
                if self.positive_args != None:
                    self.func(*self.positive_args)
            
            else:
                if self.negative_args != None:
                    self.func(*self.negative_args)