#!/bin/bash

set -e

docker container prune -f
docker container rm --force rocky8.6-pagure
rm -rf git && mkdir git

echo "All done!"
