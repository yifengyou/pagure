default:
	@echo "default    show help"
	@echo "run        run python scripts in docker"
	@echo "install    install python scripts in docker"
	@echo "check      check env whether in docker"

run: check
	PAGURE_CONFIG=/etc/pagure/pagure.cfg python3 statistic.py --debug

install: check
	cp pagure_statistic.service /usr/lib/systemd/system/pagure_statistic.service -a
	cp pagure_statistic.timer /usr/lib/systemd/system/pagure_statistic.timer -a
	systemctl daemon-reload

check:
	@[ ! -e /.dockerenv ] && echo "Fatal error! not in docker env" && exit 1 || true
