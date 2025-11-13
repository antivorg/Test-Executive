
import sys

import os_utils.posix_impl as posix_impl
import os_utils.windows_impl as windows_impl

def os_utils():
    if sys.platform.startswith("win"):
        return windows_impl.os_utils_windows()
    elif sys.platform.startswith("linux"):
        return posix_impl.os_utils_posix()
    else:
        raise NotImplementedError(f"Unsupported OS: {sys.platform}")
