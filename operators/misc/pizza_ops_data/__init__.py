import os, json, bpy
from bpy_extras.image_utils import load_image

'''
get_pizza_ops_data()

    Returns None if it fails

    Else:
        type = Dict

        Keys = json file key
        Values = bpy image, str description, str link

'''

def get_pizza_ops_data():
    '''Get the pizza ops data file.'''

    pizza_data = {}

    data_file_name = 'restaurants.txt'
    data_file_path = os.path.dirname(__file__)
    data_file_path = os.path.join(data_file_path, data_file_name)
    
    # TODO: Create a template file
    if os.path.exists(data_file_path) == False:
        os.chdir(os.path.dirname(__file__))
        open(data_file_name, 'w').close()
        print("NO FILE")
        bpy.ops.hops.display_notification(info="No file found, Created blank file.")
        return None

    try:
        folder_dir = os.path.dirname(__file__)
        files_in_folder = [f for f in os.listdir(folder_dir) if os.path.isfile(os.path.join(folder_dir, f))]

        with open(data_file_path) as f:
            data = json.load(f)

            if type(data) == dict:
                for key, val in data.items():
                    if type(val) == dict:
                        
                        keys_are_valid = False
                        if "icon" in val:
                            if "description" in val:
                                if "link" in val:
                                    keys_are_valid = True

                        if keys_are_valid == False:
                            bpy.ops.hops.display_notification(info="Check spelling on Keys in file.")
                            return None

                        raw_icon = val["icon"]
                        raw_desc = val["description"]
                        raw_link = val["link"]

                        image = None
                        for check_file in files_in_folder:
                            if raw_icon in check_file:
                                
                                image = load_image(check_file, folder_dir)
                                if image != None:
                                    pizza_data[key] = {
                                        "icon"        : image,
                                        "description" : raw_desc.title(),
                                        "link"        : raw_link
                                    }
                                else:
                                    bpy.ops.hops.display_notification(info="Make sure files are .png file types.")

    except:
        bpy.ops.hops.display_notification(info="Incorrect file format, check docs.")
        return None

    return pizza_data
