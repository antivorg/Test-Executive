
import os

from os_utils.abstract import os_utils_base

class os_utils_windows(os_utils_base):
    
    def get_tmp_folder_location():
        return f'C:\\Users\\{os.getlogin()}\\AppData\\Local\\Temp'