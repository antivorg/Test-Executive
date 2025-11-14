
import sys
import subprocess
import threading
import queue

from os_utils.os_utils import os_utils

class f_stdin_monitor:

    def __init__(self, file_descriptor):
        self._fd = file_descriptor
        self._target_file = os.readlink(self._fd)
        self._is_monitoring = False
        self._proc = None
        self._queue_stdout = None
        self._queue_stderr = None

    def start_monitoring(self):
        if self._is_monitoring:
            raise Exception(
                'start_monitoring called on a file already '
                f'being monitor {self._target_file}'
            )
        command = f'tail --follow=descriptor {self._fd}'
        self._proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            universal_newlines=True
        )
        self._queue_stdout = queue.Queue()
        self._queue_stderr = queue.Queue()
        threading.Thread(
            target=self._pipe_read_thread,
            args=(self._proc.stdout, self._queue_stdout),
            daemon=True
        ).start()
        threading.Thread(
            target=self._pipe_read_thread,
            args=(self._proc.stderr, self._queue_stderr),
            daemon=True
        ).start()
        proc_err = self._read_queue(self._queue_stderr)
        if proc_err != None:
            raise Exception(
                f'Running {command} raised the following '
                f'value of stderr: "{proc_err}"'
            )
        self._is_monitoring = True

    def stop_monitoring(self):
        if not self._is_monitoring:
            raise Exception(
                'Monitoring must be started before '
                'attempting to stop it on '
                f'{self._target_file}'
            )
        os.killpg(os.getpgid(self._proc.pid), signal.SIGTERM)
        self._is_monitoring = False

    def read_buffer(self):
        if not self._is_monitoring:
            raise Exception(
                'Attempting to read from a file that is not '
                f'currently being monitored {self._fd}'
            )
        return self._read_queue(self._queue_stdout)

    def _read_queue(self, queue):
        try:
            val = queue.get_nowait()
            return val
        except Exception as ex:
            return None

    def _pipe_read_thread(self, fd, queue):
        for line in iter(fd.readline, b''):
            queue.put(line)
        fd.close()

class dispatcher:

    def __init__(self):
        self._os_utils = os_utils
        self._available_fds = None
        self._proc = None
        self._tracked_fds = None
        self._monitor_objects = None
        self._proc_mutex = threading.Lock()
        self._stop_monitor_thread = None

    def launch_subprocess(self, command, path):
        try:
            self._proc = subprocess.Popen(
                command,
                shell=True,
                universal_newlines=True,
                cwd=path
            )
        except Exception as ex:
            # dispatcher : inform command fails(?)
            raise Exception(
                f'{sys.argv[0]}: something went wrong running the command '
                f'"{command}", "{ex}"'
            )
        self._start_monitoring_fds()

    def poll_proc(self):
        with self._proc_mutex:
            return self._proc.poll()

    def is_fd_ready(self, number):
        return False

    def get_fd(self, number):
        pass

    def _start_monitoring_fds(self):
        self._tracked_fds = []
        self._monitor_objects = {}
        self._stop_monitor_thread = Event()
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name='FD Monitor Thread'
            daemon=True
        )

    def _stop_monitoring_fds(self):
        self._stop_monitor_thread.set()
        self._monitor_thread.join(timeout=1)

    def _monitor_loop(self):
        while not self._stop_monitor_thread.is_set():
            fd_list = os.listdir(fd_path)
            new_fds = list(set(fd_list)-set(tracked_fds))
            closed_fds = list(set(tracked_fds)-set(fd_list))
            for new_fd in new_fds:
                print(f'New FD: {new_fd}')
                tracked_fds.append(new_fd)
                monitor_objects[new_fd] = [
                    os.readlink(fd_path+new_fd).split(os.sep)[-1],
                    f_stdin_monitor(fd_path+new_fd)
                ]
                monitor_objects[new_fd][1].start_monitoring()
                name = monitor_objects[new_fd][0]
                print('Started Monitoring: {name} (FD {new_fd})')
            for fd in monitor_objects:
                name = monitor_objects[fd][0]
                print(f'Reading: {name} (FD {fd})')
                monitor = monitor_objects[fd][1]
                line = monitor.read_buffer()
                line = line.replace('\n', '') if line else ''
                print(f'Line[{line}]')
            for old_fd in closed_fds:
                name = monitor_objects[old_fd][0]
                print(f'Ceasing Monitoring: {name} (FD {old_fd})')
                monitor_objects[old_fd][1].stop_monitoring()
            time.sleep(0.1)
        for fd in monitor_objects:
            monitor_objects[fd][1].stop_monitoring()
