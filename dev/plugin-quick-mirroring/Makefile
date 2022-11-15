default:
	@echo "default    show help"
	@echo "run        run python scripts in docker"
	@echo "install    install python scripts in docker"
	@echo "check_env  check_env env whether in docker"
	@echo "status     get reference env status"

run: check_env
	PAGURE_CONFIG=/etc/pagure/pagure.cfg python3 quick_mirroring.py --debug

install: check_env
	cp pagure_quick_mirroring.service /usr/lib/systemd/system/pagure_quick_mirroring.service -a
	cp pagure_quick_mirroring.timer /usr/lib/systemd/system/pagure_quick_mirroring.timer -a
	systemctl daemon-reload

status: check_env
	ps aux|grep -E 'src-openeuler|git push local'
	echo "total:"`ls -d /home/git/repositories/src-openeuler/*.git |wc -l`
	cd  /home/git/repositories/src-openeuler/
	echo "left:"`find ./ -name heads -empty |wc -l`
	find ./ -name heads -empty 

check_env:
	@[ ! -e /.dockerenv ] && echo "Fatal error! not in docker env" && exit 1 || true

