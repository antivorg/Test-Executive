
import sys
import time

class script_runner:

    def __init__(self, config):
        self._config = config
        self._thread_dict = None
        self._proc = None

    def load_config(self):
        self._thread_dict = {}
        for script_id in self._config['scripts']:
            script_fields = self._config['scripts'][script_id]
            for field in ['name', 'command', 'path']
                if not field in script_fields:
                    print(
                        f'{sys.argv[0]}: YAML missing key "{field}:" in '
                        f'"file_descriptors:{script_id}:"'
                    )
                    return -1
                if script_fields[field] == None:
                    print(
                        f'{sys.argv[0]}: YAML missing value for key '
                        f'"file_descriptors:{script_id}:{script_fields}:"'
                    )
                    return -1
                setattr(self, script_id, script_id)
                self._thread_dict[script_id] = script_fields
        self._config_loaded = True
        return 0

    def run_command(self, command, blocking=False):
        command_params = self._thread_dict[command]
        # dispatcher : about to launch command
        self._dispatcher.launch_subprocess(
            command_params['command'],
            command_params['path']
        )
        # dispatcher : tell it to latch on to FD's
        if blocking:
            while self._dispatcher.poll_proc() == None:
                time.sleep(0.5)

    def command_still_running(self):
        if self._dispatcher.poll_proc() == None:
            return True
        else:
            False

    def get_return_code(self):
        return self._dispatcher.poll_proc()
