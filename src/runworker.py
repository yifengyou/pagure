#!/usr/bin/env python3

from __future__ import unicode_literals, absolute_import

import argparse
import sys
import os
import subprocess


parser = argparse.ArgumentParser(description="Run the Pagure worker")
# argparse 会把我们传递给它的选项默认都视作为字符串，除非参数指定，例如type=int
# action本质是bool类型。这意味着，当这一选项存在时，为 args.verbose 赋值为 True。没有指定时则隐含地赋值为 False。
# action两种值：action=‘store_false’ 和 action=‘store_true’
# store_true就代表着一旦指令里写了这个参数，那么将其值设为True，没有时，默认状态下其值为False。
# 同理：store_false代表一旦命令中有此参数，其值则变为False，默认为True。
# dest：如果提供dest，例如dest=“datapath”，那么可以通过args.datapath访问该参数
parser.add_argument(
    "--config",
    "-c",
    dest="config",
    help="Configuration file to use for pagure.",
)
parser.add_argument(
    "--debug",
    dest="debug",
    action="store_true",
    default=False,
    help="Expand the level of data returned.",
)
parser.add_argument(
    "--queue",
    dest="queue",
    default=None,
    help="Name of the queue to run the worker against.",
)

# 指定任务入口
parser.add_argument(
    "--tasks",
    dest="tasks",
    default="pagure.lib.tasks",
    help="Class used by the workers.",
)
parser.add_argument(
    "--noinfo",
    dest="noinfo",
    action="store_true",
    default=False,
    help="Reduce the log level.",
)

args = parser.parse_args()

env = os.environ
if args.config:
    config = args.config
    if not config.startswith("/"):
        here = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        config = os.path.join(here, config)
    env["PAGURE_CONFIG"] = config

# 解决高版本celery命令解析变更问题，调整顺序即可
# cmd = [sys.executable, "-m", "celery", "-A", args.tasks, "worker"]
cmd = [sys.executable, "-m", "celery",  "-A", args.tasks, "worker"]
print(str(cmd))

if args.queue:
    cmd.extend(["-Q", args.queue])

if args.debug:
    cmd.append("--loglevel=debug")
elif args.noinfo:
    pass
else:
    cmd.append("--loglevel=info")

subp = subprocess.Popen(cmd, env=env or None)
subp.wait()
