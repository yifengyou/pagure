#!/bin/bash

#ps aux|grep -E "git clone|git push"
ps aux|grep -E 'src-openeuler|git push local'
echo "total:"`ls -d /home/git/repositories/src-openeuler/*.git |wc -l`
cd  /home/git/repositories/src-openeuler/
echo "left:"`find ./ -name heads -empty |wc -l`
find ./ -name heads -empty 
