#!/bin/bash

set -x

dnf config-manager --add-repo=https://download.docker.com/linux/fedora/docker-ce.repo
dnf install docker-ce -y
systemctl enable --now docker

echo "All done!"
