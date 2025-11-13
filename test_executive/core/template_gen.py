
import os
import sys

GEN_PATH = 'gen' + os.sep

def template_gen(config):
    # Create lib file
    if config['thread_library'] == None:
        print(
            f'{sys.argv[0]}: YAML missing thread library definition '
            '"thread_lib:"'
        )
        return -1
    gen_file_contents = '\nfrom threading import Lock, local\nfrom queue '
    gen_file_contents += 'import Queue, LifoQueue, PriorityQueue\nfrom '
    gen_file_contents += 'collections import deque\n\n# This file has been '
    gen_file_contents += 'automatically generated'
    for thread_key in config['threads']:
        thread = config['threads'][thread_key]
        if not 'thread_definition' in thread:
            print(
                f'{sys.argv[0]}: YAML missing '
                '"threads:{thread_key}:thread_definition"'
            )
            return -1
        gen_file_contents += f'\n\n\ndef {thread["thread_definition"]}'
        gen_file_contents += '(thread_io_dict):\n\t\'\'\'\n\t\t'
        gen_file_contents += 'thread_io_dict:\n\t\t- type: <dict>\n\t\t'
        gen_file_contents += '- entrys:'
        if not 'io_binds' in thread:
            print(
                f'{sys.argv[0]}: YAML missing '
                '"threads:{thread_key}:io_binds"'
            )
            return -1
        if type(thread['io_binds']) != list:
            print(
                f'{sys.argv[0]}: YAML type '
                '"threads:{thread_key}:io_binds" must be list'
            )
            return -1
        file_contents_assert = '\n\twith thread_io_dict["test_mutex"]:'
        for io in thread['io_binds']:
            io_type_value = None
            for io_type in config['io_objects']:
                if io_type == io:
                    io_type_value = config['io_objects'][io_type]['type']
            if io_type_value == None:
                print(
                    f'{sys.argv[0]}: YAML could not find "{io}" bind '
                    f'key value in "io_objects:"'
                )
                return -1
            gen_file_contents += f'\n\t\t\t{io}: type=<{io_type_value}>'
            if not io_type_value in ['Lock', 'NoneType']:
                file_contents_assert += f'\n\t\tassert(type(thread_io_dict['
                file_contents_assert += f'"{io}"])=={io_type_value})'
        gen_file_contents += '\n\t\'\'\''
        gen_file_contents += file_contents_assert
        gen_file_contents += '\n\tpass'
    with open(GEN_PATH + config['thread_library'] + '.py', 'w+') as file:
        file.write(gen_file_contents)

