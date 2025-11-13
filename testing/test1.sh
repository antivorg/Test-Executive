#! /bin/bash

sigint_handler() {
    dirs -c
}
trap sigint_handler SIGINT

pushd "$(dirname "$0")" >/dev/null

pushd ../test_executive/ >/dev/null
python3 test_executive.py -t ../configurations/test1.yaml
rm plugins/thread_lib_1.py >/dev/null
cp plugins/gen/thread_lib_1.py plugins/ >/dev/null
python3 test_executive.py ../configurations/test1.yaml

dirs -c
