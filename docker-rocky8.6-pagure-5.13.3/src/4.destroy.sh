#!/bin/bash

set -e

docker container prune -f
docker container rm --force rocky8.6-pagure
#rm -rf home-git && mkdir home-git

echo "All done!"
