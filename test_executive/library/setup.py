
import sys
import os
import argparse
import yaml
from filelock import FileLock, Timeout

from os_utils.os_utils import os_utils

GOLDEN_REFERENCE_CONF = sys.path[0] + os.sep + 'conf' + os.sep
GOLDEN_REFERENCE_CONF += 'golden_reference.yaml'

def handle_cmdline_parameters():
    '''
        Parse/handle command line arguments
    '''
    parser = argparse.ArgumentParser(
        description = 'Test Executive - A fully configurable GUI for test '\
                        'running/automation/regression.'
    )
    parser.add_argument(
        'config', help='path to YAML Test Executive configuration',
        type=str
    )
    parser.add_argument(
        '-g', '--golden-config',
        help='use a custom yaml file FILE_NAME defining required fields',
        action='store', metavar='FILE_NAME'
    )
    parser.add_argument(
        '-m', '--minimised', help='launch the Test Executive minimised', 
        action='store_true'
    )
    parser.add_argument(
        '-t', '--template', help='for the given config file, create a '\
                                    'bare thread library file in '\
                                    '/plugins/gen with headers based on '\
                                    'the chosen config',
        action='store_true'
    )
    parser.add_argument(
        '-v', '--version', help='version number',
        action='version', version='%(prog)s 1.0'
    )
    return parser.parse_args()

def handle_config_file(cmdline_args, user_dir):
    '''
        Load and validate the YAML configuration file "cmdline_args.config"
            - cmdline_args      : An "argparse.Namespace" object
    '''
    # load yaml
    conf_file_path = user_dir + '/' + cmdline_args.config
    if not os.path.isfile(conf_file_path):
        print(
            f'{sys.argv[0]}: Failed to open config file '
            f'"{conf_file_path}"'
        )
        return None, -1
    try:
        with open(conf_file_path) as conf_file:
            config = yaml.safe_load(conf_file)
    except Exception as ex:
        print(
            f'{sys.argv[0]}: Failed to parser YAML of '
            f'"{conf_file_path}" with Exception {ex}'
        )
        return None, -1
    
    # load golden reference yaml
    golden_reference_conf = GOLDEN_REFERENCE_CONF   
    if cmdline_args.golden_config != None:
        golden_reference_conf = cmdline_args.golden_config
    if not os.path.isfile(golden_reference_conf):
        print(
            f'{sys.argv[0]}: Failed to open config file '
            f'"{golden_reference_conf}"'
        )
        return None, -1
    try:
        with open(golden_reference_conf) as conf_file:
            golden_config = yaml.safe_load(conf_file)
    except Exception as ex:
        print(
            f'{sys.argv[0]}: Failed to parser YAML of '
            f'"{golden_reference_conf}" with Exception {ex}'
        )
        return None, -1

    # validate against golden reference
    status, failed_stack = recursively_compare_configs(
        golden_config, config
    )
    if status == -1:
        if failed_stack[-1] == ':':
            print(
                f'{sys.argv[0]}: Missing key in "{cmdline_args.config}", '
                f'expecting: "{failed_stack}"'
            )
            return None, -1
        else:
            print(
                f'{sys.argv[0]}: Missing or incorrect value in '
                f'"{cmdline_args.config}", expecting: "{failed_stack}"'
            )
            return None, -1
    return config, 0

def recursively_compare_configs(golden_config, config):
    '''
        Recursively confirm all keys/values featured in "golden_config"
        are present in "config"
            - golden_config     : Dictionary containing keys/value to find
            - config            : Dictionary to be validated
    '''
    for key in golden_config:
        if not key in config:
            return -1, f'{key}:'
        if golden_config[key] == None:
            continue
        if type(golden_config[key]) == dict:
            # Recursion, handling nested dictionaries
            status, failed_stack = recursively_compare_configs(
                golden_config[key], config[key]
            )
            if status == -1:
                return status, f'{key}:{failed_stack}'
        else:
            if golden_config[key] != config[key]:
                return -1, golden_config[key]
    return 0, ''

def acquire_lock_file():
    os_dep = os_utils()
    temp_dir = os_dep.get_tmp_folder_location() + os.sep + 'test_executive'
    lock_file = temp_dir + os.sep + 'test_exec_state.txt.lock'
    if os.path.isdir(temp_dir):
        # last instance didn't close propperly
        # check for file lock
        lock = FileLock(lock_file, timeout=0.3)
        try: lock.acquire()
        except Timeout:
            print(f'Another instance of {sys.argv[1]} is already open')
            return -1
    else:
        # nominal, create a lock file
        os.mkdir(temp_dir)
        lock = FileLock(lock_file, timeout=1)
        try: lock.acquire()
        except Timout:
            print(f'Something went wrong creating lock file {lock_file}')
            return -1
    return 0

def release_lock_file():
    os_dep = os_utils()
    temp_dir = os_dep.get_tmp_folder_location() + os.sep + 'test_executive'
    lock_file = temp_dir + os.sep + 'test_exec_state.txt.lock'
    lock = FileLock(lock_file, timeout=0.3)
    lock.release()
    os.remove(lock_file)
    os.rmdir(temp_dir)
    return 0
