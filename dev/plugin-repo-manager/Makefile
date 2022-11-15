default:
	@echo "default    show help"
	@echo "run        run python scripts in docker"
	@echo "install    install python scripts in docker"
	@echo "check_env  check_env env whether in docker"
	@echo "status     get reference env status"

run: check_env
	PAGURE_CONFIG=/etc/pagure/pagure.cfg python3 repo_manager.py --debug

install: check_env
	cp pagure_repo_manager.service /usr/lib/systemd/system/pagure_repo_manager.service -a
	cp pagure_repo_manager.timer /usr/lib/systemd/system/pagure_repo_manager.timer -a
	systemctl daemon-reload

status: check_env
	ps aux|grep -E 'src-openeuler|git push local'
	echo "total:"`ls -d /home/git/repositories/src-openeuler/*.git |wc -l`
	cd  /home/git/repositories/src-openeuler/
	echo "left:"`find ./ -name heads -empty |wc -l`
	find ./ -name heads -empty 

check_env:
	@[ ! -e /.dockerenv ] && echo "Fatal error! not in docker env" && exit 1 || true

