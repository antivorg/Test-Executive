
from abc import ABC, abstractmethod

class os_utils_base(ABC):

    @abstractmethod
    def get_tmp_folder_location(self):
        raise NotImplementedError()
