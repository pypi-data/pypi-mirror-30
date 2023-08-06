#!/bin/bash
# (cc) 2016 diamond-patterns

if [ -f /usr/local/rvm/scripts/rvm ]; then
    source /usr/local/rvm/scripts/rvm
fi

echo "publish site"
GIT_DIR=~/site/.git
cd ~/site && git pull
cd ~/site && make build install
echo "OK"
