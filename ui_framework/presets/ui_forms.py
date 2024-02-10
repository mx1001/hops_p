
class Main_Panel_Form:

    def __init__(self):
        '''
        Support 6 boxes in the main banner.
        c = Column
        r = Row

                c1 c2  c3     
                |  |   |
                v  V   V  

       r1 ->   | 1  3  5 |
               | 2  4  6 |

        '''

        self.one_ON = True
        self.one_width_percent = 33.33
        self.one_text = ""
        self.one_image = ""
        self.one_func = None
        self.one_positive_args = None
        self.one_negative_args = None
        self.one_drag = False

        self.two_ON = True
        self.two_text = ""
        self.two_image = ""
        self.two_func = None
        self.two_positive_args = None
        self.two_negative_args = None
        self.two_drag = False

        self.three_ON = True
        self.three_width_percent = 33.33
        self.three_text = ""
        self.three_image = ""
        self.three_func = None
        self.three_positive_args = None
        self.three_negative_args = None
        self.three_drag = False

        self.four_ON = True
        self.four_text = ""
        self.four_image = ""
        self.four_func = None
        self.four_positive_args = None
        self.four_negative_args = None
        self.four_drag = False

        self.five_ON = True
        self.five_width_percent = 33.33
        self.five_text = ""
        self.five_image = ""
        self.five_func = None
        self.five_positive_args = None
        self.five_negative_args = None
        self.five_drag = False

        self.six_ON = True
        self.six_text = ""
        self.six_image = ""
        self.six_func = None
        self.six_positive_args = None
        self.six_negative_args = None
        self.six_drag = False


class Mods_Panel_Form:

    def __init__(self):

        self.left_width_percent = 10
        self.left_text = ""
        self.left_func = None
        self.left_positive_args = None
        self.left_negative_args = None
        self.left_drag = False

        self.center_width_percent = 65
        self.center_text = ""
        self.center_func = None
        self.center_positive_args = None
        self.center_negative_args = None
        self.center_drag = False

        self.right_width_percent = 25
        self.right_text = ""
        self.right_func = None
        self.right_positive_args = None
        self.right_negative_args = None
        self.right_drag = False
