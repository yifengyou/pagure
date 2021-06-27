#!/bin/bash

if [ -f /var/tmp/pagure_dev.sqlite ];then
	rm -rf /var/tmp/pagure_dev.sqlite
	echo "clean sqlite:////var/tmp/pagure_dev.sqlite"
fi

if [ -d lcl ];then
	rm -rf lcl
	echo "remove lcl dir"
	mkdir -p lcl/{repos,remotes,attachments,releases}
	echo "mkdir -p lcl/{repos,remotes,attachments,releases}"
fi
