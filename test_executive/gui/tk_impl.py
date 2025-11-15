
import sys
import tkinter as tk
import tkinter.ttk as ttk
import copy

class command:
    def __init__(self, value):
        self._value = value
    def send(self):
        print(self._value)

class gui:

    def __init__(self):
        self._root = tk.Tk()
        self._root.title('Test-Executive')
        self._root.configure(background="white")
        #self._root.minsize(200, 200)
        #self._root.maxsize(500, 500)
        #self._root.geometry("300x300+50+50")


    def set_widget(self, wtype, widget_args, grid_args):
        func = getattr(tk, wtype)
        func(self._root, **widget_args).grid(**grid_args)

    def configure(self, config, queue):
        self._command_queue = queue
        for key in config['window']:
            widget_params = config['window'][key]
            for expected_key in ['type', 'args', 'grid']:
                if not expected_key in widget_params:
                    print(
                        f'{sys.argv[0]} YAML missing "{expected_key}" key '
                        f'in "window:{key}:"'
                    )
                    return -1
                if widget_params[expected_key] == None:
                    print(
                        f'{sys.argv[0]}: YAML missing value for key '
                        f'"window:{key}:{expected_key}"'
                    )
                    return -1
            if 'command' in widget_params['args']:
                cmd = widget_params['args']['command']
                command_object = command(cmd)
                widget_params['args']['command'] = command_object.send
            self.set_widget(
                widget_params['type'],
                widget_params['args'],
                widget_params['grid']
            )
        return 0

    def main_loop(self):
        self._root.mainloop()

