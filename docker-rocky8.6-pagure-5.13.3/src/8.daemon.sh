#!/bin/bash

set -e

docker container prune -f

[ ! -d home-git ] && mkdir home-git

docker run --privileged -d -v `pwd`/home-git:/home/git -p 8880:8880 -p 8822:22 --name rocky8.6-pagure rockylinux8.6-pagure /usr/sbin/init

echo "All done!"
