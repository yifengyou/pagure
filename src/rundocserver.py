#!/usr/bin/env python

from __future__ import unicode_literals, absolute_import

# These two lines are needed to run on EL6
__requires__ = ["jinja2 >= 2.4"]
import pkg_resources

import argparse
import sys
import os


parser = argparse.ArgumentParser(description="Run the Pagure doc server")
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
    help="Configuration file to use for the pagure doc server.",
)
parser.add_argument(
    "--debug",
    dest="debug",
    action="store_true",
    default=False,
    help="Expand the level of data returned.",
)
parser.add_argument(
    "--profile",
    dest="profile",
    action="store_true",
    default=False,
    help="Profile the doc server.",
)
parser.add_argument(
    "--port",
    "-p",
    default=5001,
    help="Port for the Pagure doc server to run on.",
)
parser.add_argument(
    "--host",
    default="0.0.0.0", # 替换默认的127.0.0.1
    help="Hostname to listen on. When set to 0.0.0.0 the server is "
    "available externally. Defaults to 127.0.0.1 making the it only "
    "visible on localhost",
)

args = parser.parse_args()

if args.config:
    config = args.config
    if not config.startswith("/"):
        here = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        config = os.path.join(here, config)
    os.environ["PAGURE_CONFIG"] = config

# 关键函数
from pagure.docs_server import APP

if args.profile:
    # from werkzeug.contrib.profiler import ProfilerMiddleware 旧版本
    from werkzeug.middleware.profiler import ProfilerMiddleware

    APP.config["PROFILE"] = True
    APP.wsgi_app = ProfilerMiddleware(APP.wsgi_app, restrictions=[30])

APP.debug = True
# 打印所有路由信息
print(APP.url_map)
APP.run(host=args.host, port=int(args.port))
