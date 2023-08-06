#!/bin/bash

# boostrap a host that does not already have a sudo-capable Ansible user

# usage:
# bin/bootstrap.sh [hostname]

# edit ./inventory
# ensure hostname ansible_user is a sudoable, non-root user

# before use, install dependencies:
# make depends

if [ ! -z $1 ]; then
    ansible-playbook ./bootstrap.yaml --extra-vars "target=$1" -k --ask-become-pass
fi
