#!/usr/bin/env python3

###############################################################################
# Please note that this script is only used for development purposes.         #
# Do not start the Flask app with this script in a production environment,    #
# use files/pagure.wsgi instead!                                              #
###############################################################################

from __future__ import unicode_literals, absolute_import

import argparse
import sys
import os

parser = argparse.ArgumentParser(description="Run the Pagure app")
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
    "--plugins",
    dest="plugins",
    help="Configuration file for pagure plugins. This argument takes "
    "precedence over the environment variable PAGURE_PLUGINS_CONFIG, which in "
    "turn takes precedence over the configuration variable "
    "PAGURE_PLUGINS_CONFIG.",
)
parser.add_argument(
    "--debug",
    dest="debug",
    action="store_true",
    default=False, # 默认开启调试
    help="Expand the level of data returned.",
)
parser.add_argument(
    "--profile",
    dest="profile",
    action="store_true",
    default=False,
    help="Profile Pagure.",
)
parser.add_argument(
    "--perf-verbose",
    dest="perfverbose",
    action="store_true",
    default=False,
    help="Enable per-request printing of performance statistics.",
)
parser.add_argument(
    "--port", "-p",
    default=5000,
    help="Port for the Pagure to run on."
)
parser.add_argument(
    "--no-debug",
    action="store_true",
    help="Disable debugging"
)
parser.add_argument(
    "--host",
    default="0.0.0.0", # 调整为0.0.0.0
    help="Hostname to listen on. When set to 0.0.0.0 the server is available "
    "externally. Defaults to 127.0.0.1 making the it only visible on localhost",
)

args = parser.parse_args()

if args.config:
    config = args.config
    if not config.startswith("/"):
        here = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        config = os.path.join(here, config)
    # 指定配置路径，写到环境变量PAGURE_CONFIG
    os.environ["PAGURE_CONFIG"] = config
    print("Using configfiel [%s]" % config)

if args.plugins:
    config = args.plugins
    if not config.startswith("/"):
        here = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        config = os.path.join(here, config)

    # 指定插件配置路径，PAGURE_PLUGINS_CONFIG与PAGURE_PLUGIN（旧版本）等价
    os.environ["PAGURE_PLUGINS_CONFIG"] = config
    print("Using configfiel [%s]" % config)
    # If this script is ran with the deprecated env. variable PAGURE_PLUGIN
    # and --plugins, we need to override it too.
    if "PAGURE_PLUGIN" in os.environ:
        os.environ["PAGURE_PLUGIN"] = config

# 配置详细输出
if args.perfverbose:
    os.environ["PAGURE_PERFREPO"] = "true"
    os.environ["PAGURE_PERFREPO_VERBOSE"] = "true"

# app入口，create_app
from pagure.flask_app import create_app

# 创建Flask应用
APP = create_app()

# 是否启用性能检测模块
# werkzeug.middleware.profiler.ProfilerMiddleware中间件对Flask的每个请求进行性能分析
if args.profile:
    # from werkzeug.contrib.profiler import ProfilerMiddleware 旧版本
    from werkzeug.middleware.profiler import ProfilerMiddleware

    APP.config["PROFILE"] = True
    APP.wsgi_app = ProfilerMiddleware(APP.wsgi_app, restrictions=[30])

APP.debug = not args.no_debug
# 打印所有路由信息
print(APP.url_map)
APP.run(host=args.host, port=int(args.port))
