
import os
import sys
import threading
import queue
import collections
import importlib
import traceback

THREAD_LIB_PATH = 'plugins' + os.sep

def return_none():
    pass

class thread_model:

    _supported_io_objects = {
        # imported types useful for threading
        'Queue'             : queue.Queue,
        'LifoQueue'         : queue.LifoQueue,
        'PriorityQueue'     : queue.PriorityQueue,
        'deque'             : collections.deque,
        'Lock'              : threading.Lock,
        'Condition'         : threading.Condition,
        'Semaphore'         : threading.Semaphore,
        'Event'             : threading.Event,
        'local'             : threading.local,
        # generic built-ins, supporting defaults
        'str'               : str,
        'int'               : int,
        'float'             : float,
        'complex'           : complex,
        'list'              : list,
        'dict'              : dict,
        'set'               : set,
        'bool'              : bool,
        'bytes'             : bytes,
        'bytearray'         : bytearray,
        'NoneType'          : return_none
    }

    def __init__(self, config):
        self._config = config
        self._io_dict = None
        self._fd_dict = None
        self._threads = None
        self._error_dict = None

    def create_io_objects(self):
        self._io_dict = {}
        for io_object_name in self._config['io_objects']:
            io_object = self._config['io_objects'][io_object_name]
            if not 'type' in io_object:
                print(
                    f'{sys.argv[0]}: YAML cannot find '
                    f'"io_objects:{io_object_name}:type"'
                )
                return -1
            if not io_object['type'] in self._supported_io_objects:
                print(
                    f'{sys.argv[0]}: YAML '
                    f'"io_objects:{io_object_name}:type" is not '
                    f'supported "{io_object["type"]}"'
                )
                return -1
            obj = self._supported_io_objects[io_object['type']]()
            self._io_dict[io_object_name] = obj
        return 0

    def create_fd_funcs(self):
        self._fd_dict = {}
        contents = ''
        for fd_number in self._config['file_descriptors']:
            fd_params = self._config['file_descriptors'][fd_number]
            for field in ['name', 'label', 'io_binds']:
                if not field in fd_params:
                    print(
                        f'{sys.argv[0]}: YAML missing key "{field}:" in '
                        f'"file_descriptors:{fd_number}:"'
                    )
                    return -1
                if fd_params[field] == None:
                    print(
                        f'{sys.argv[0]}: YAML missing value for key '
                        f'"file_descriptors:{fd_number}:{field}:"'
                    )
                    return -1
            name = fd_params['label']
            self._fd_dict[name] = {
                'name': fd_params['name'],
                'io_binds':{}
            }
            for io in fd_params['io_binds']:
                self._fd_dict[name]['io_binds'][io] = self._io_dict[io]
        return 0

    def create_thread_model(self):
        self._threads = []
        self._error_dict = {
            'lock':threading.Lock(),
            'thread_error_stack':[]
        }
        # Create user threads
        if self._config['thread_library'] == None:
            print(
                f'{sys.argv[0]}: YAML no "thread_library:" value defined'
            )
            return -1
        try:
            thread_lib_module = importlib.import_module(
                THREAD_LIB_PATH.replace(os.sep, '.') +
                self._config['thread_library']
            )
        except ModuleNotFoundError as ex:
            print(
                f'{sys.argv[0]}: Failed to open module "{THREAD_LIB_PATH}'
                f'{self._config["thread_library"]}" as defined in'
                f'"{self._config["thread_library"]}" {ex}'
            )
            return -1
        for thread_key in self._config['threads']:
            thread = self._config['threads'][thread_key]
            arg_dict = {}
            for arg in thread['io_binds']:
                if not arg in self._io_dict:
                    print(
                        f'{sys.argv[0]}: YAML io_binds '
                        f'"threads:{thread}:io_binds" value {arg} is not '
                        'in io_ojbects:'
                    )
                    return -1
                arg_dict[arg] = self._io_dict[arg]
            try:
                func = getattr(
                    thread_lib_module,
                    thread['thread_definition']
                )
            except AttributeError as ex:
                print(
                    f'{sys.argv[0]}: missing thread/function definition '
                    'for "threads:{thread}:thread_definition:" value '
                    f'"{thread["thread_definition"]}" {ex}'
                )
                return -1
            self._threads.append(
                threading.Thread(
                    target=self._thread_wrapper,
                    name=thread['name'],
                    args=(
                        func, arg_dict, self._error_dict, thread['name']
                    ),
                    daemon=thread['daemon']
                )
            )
        # Create file descriptor threads
        for fd_key in self._fd_dict:
            fd = self._fd_dict[fd_key]
            self._threads.append(
                threading.Thread(
                    target=self._thread_wrapper,
                    name=fd['name'],
                    args=(
                        self._thread_fd, fd['io_binds'],
                        self._error_dict, fd['name']
                    ),
                    daemon=True
                )
            )
        return 0

    def run(self):
        for thread in self._threads:
            thread.start()

    def _thread_wrapper(self, func, arg_dict, error_dict, name):
        try: func(arg_dict)
        except Exception as ex:
            with self._error_dict['lock']:
                self._error_dict.append({
                    'thread':name,
                    'exception':ex,
                    'call_stack':traceback.format_exc()
                })

    def _thread_fd(self, dict):
        pass

class thread_manager:

    def __init__(self, config):
        self._thread_model = thread_model(config)

    def thread_init(self):
        status = self._thread_model.create_io_objects()
        if status == 0:
            status = self._thread_model.create_fd_funcs()
        if status == 0:
            status = self._thread_model.create_thread_model()
        return status

    def launch_application(self):
        try: self._thread_model.run()
        except Exception as ex:
            print(
                f'{sys.argv[0]}: something went wrong launching the '
                f'application "{ex}"'
            )
            return -1
        return 0

    def monitor_application(self):
        pass

