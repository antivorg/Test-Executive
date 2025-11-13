
import os
import sys

if __name__ == '__main__':
    #handle paths
    user_dir = os.getcwd()
    os.chdir(sys.path[0])

import lib.setup as setup
import core.thread_manager as thread_manager
import core.template_gen as template_gen


if __name__ == '__main__':
    # input handling
    cmdline_args = setup.handle_cmdline_parameters()
    # handle lock file
    status = setup.acquire_lock_file()
    # processes yaml
    if status == 0:
        config, status = setup.handle_config_file(cmdline_args, user_dir)
    if cmdline_args.template:
        # special argument -t, if set just create a template file
        if status == 0:
            status = template_gen.template_gen(config)
    else:
        # set-up application
        if status == 0:
            thread_manager_obj = thread_manager.thread_manager(config)
            status = thread_manager_obj.thread_init()
        # launch application
        if status == 0:
            status = thread_manager_obj.launch_application()
        while status == 0:
            status = thread_manager_obj.monitor_application()
    # release lock file
    setup.release_lock_file()

    exit(status)
