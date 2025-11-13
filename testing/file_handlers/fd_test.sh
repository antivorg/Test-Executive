#! /bin/bash

python3 -u open_fd.py > file2.txt & pid=$!

echo Launched Process: $pid

python3 fd_test.py $pid

kill $pid

echo DONE

