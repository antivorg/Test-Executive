#! /bin/bash

sigint_handler() {
    dirs -c
}
trap sigint_handler SIGINT

pushd "$(dirname "$0")" >/dev/null

pushd ../test_executive/ >/dev/null
python3 test_executive.py ../conf/test2.yaml

dirs -c
