import sys
import os
import subprocess
import threading
import signal
import queue
import time

class f_stdin_monitor:
    '''
        Monitor and read what's been written to an open FD's
        STDIN
    '''

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

def proc_track_file_descrpitors(pid):
    if not pid in os.listdir('/proc/'):
        return
    tracked_fds = []
    monitor_objects = {}
    fd_path = f'/proc/{pid}/fd/'
    while True:
        print(f'Tracked fd\'s: {tracked_fds}')
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

if __name__ == '__main__':
    proc_track_file_descrpitors(sys.argv[1])

