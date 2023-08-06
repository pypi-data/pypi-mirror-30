# -*- coding: utf-8 -*-
# vim: set ts=4

# Copyright 2017 Rémi Duraffort
# This file is part of lavacli.
#
# lavacli is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# lavacli is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with lavacli.  If not, see <http://www.gnu.org/licenses/>

import argparse
import yaml

from . import jobs


def configure_parser(parser):
    sub = parser.add_subparsers(dest="sub_sub_command", help="Sub commands")
    sub.required = True

    # "logs"
    logs = sub.add_parser("logs", help="log helpers")
    logs_sub = logs.add_subparsers(dest="sub_sub_sub_command",
                                   help="Sub commands")
    logs_sub.required = True

    # "logs.print"
    logs_print = logs_sub.add_parser("print",
                                     help="print log file")
    logs_print.add_argument("filename",
                            type=argparse.FileType('r'),
                            help="log file")
    logs_print.add_argument("--filters", default=None, type=str,
                            help="comma seperated list of levels to show")
    logs_print.add_argument("--raw", default=False, action="store_true",
                            help="print raw logs")

def help_string():
    return "utility functions"


def handle_logs(proxy, options):
    try:
        logs = yaml.load(options.filename.read(), Loader=yaml.CLoader)
    except yaml.YAMLError:
        print("Invalid yaml file")
    else:
        jobs.print_logs(logs, options.raw, options.filters)


def handle(proxy, options, _):
    handlers = {
        "logs": handle_logs,
    }
    return handlers[options.sub_sub_command](proxy, options)
