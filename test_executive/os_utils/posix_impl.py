
from os_utils.abstract import os_utils_base

class os_utils_posix(os_utils_base):

    def get_tmp_folder_location(self):
        return '/tmp'