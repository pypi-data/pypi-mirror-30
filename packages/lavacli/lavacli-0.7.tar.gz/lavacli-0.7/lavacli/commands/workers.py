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
import time
import yaml


def configure_parser(parser):
    sub = parser.add_subparsers(dest="sub_sub_command", help="Sub commands")
    sub.required = True

    # "add"
    workers_add = sub.add_parser("add", help="add a worker")
    workers_add.add_argument("hostname", type=str,
                             help="worker hostname")
    workers_add.add_argument("--description", type=str, default=None,
                             help="worker description")
    workers_add.add_argument("--disabled", action="store_true",
                             default=False, help="create a disabled worker")

    # "config"
    workers_config = sub.add_parser("config", help="worker configuration")
    config_sub = workers_config.add_subparsers(dest="sub_sub_sub_command",
                                               help="Sub commands")
    config_sub.required = True
    config_get = config_sub.add_parser("get",
                                       help="get the worker configuration")
    config_get.add_argument("hostname", type=str,
                            help="worker hostname")

    config_set = config_sub.add_parser("set",
                                       help="set the worker configuration")
    config_set.add_argument("hostname", type=str,
                            help="worker hostname")
    config_set.add_argument("config", type=argparse.FileType('r'),
                            help="configuration file")

    # "list"
    workers_list = sub.add_parser("list", help="list workers")
    workers_list.add_argument("--yaml", dest="output_format",
                              action="store_const", const="yaml",
                              default=None, help="print as yaml")

    # "maintenance"
    workers_maintenance = sub.add_parser("maintenance",
                                         help="maintenance the worker")
    workers_maintenance.add_argument("hostname", type=str,
                                     help="worker hostname")
    workers_maintenance.add_argument("--force", default=False,
                                     action="store_true",
                                     help="force worker maintenance by canceling running jobs")
    workers_maintenance.add_argument("--no-wait", dest="wait",
                                     default=True, action="store_false",
                                     help="do not wait for the devices to be idle")

    # "update"
    update_parser = sub.add_parser("update", help="update worker properties")
    update_parser.add_argument("hostname", type=str,
                               help="worker hostname")
    update_parser.add_argument("--description", type=str, default=None,
                               help="worker description")
    update_parser.add_argument("--health", type=str, default=None,
                               choices=["ACTIVE", "MAINTENANCE", "RETIRED"],
                               help="worker health")

    # "show"
    workers_show = sub.add_parser("show", help="show worker details")
    workers_show.add_argument("hostname", help="worker hostname")
    workers_show.add_argument("--yaml", dest="output_format",
                              action="store_const", const="yaml",
                              default=None, help="print as yaml")


def help_string():
    return "manage workers"


def handle_add(proxy, options):
    proxy.scheduler.workers.add(options.hostname,
                                options.description,
                                options.disabled)


def handle_config(proxy, options):
    if options.sub_sub_sub_command == "get":
        config = proxy.scheduler.workers.get_config(options.hostname)
        print(str(config).rstrip("\n"))
    else:
        config = options.config.read()
        ret = proxy.scheduler.workers.set_config(options.hostname,
                                                 config)
        if not ret:
            print("Unable to store worker configuration")
            return 1


def handle_list(proxy, options):
    workers = proxy.scheduler.workers.list()
    if options.output_format == "yaml":
        print(yaml.dump(workers).rstrip("\n"))
    else:
        print("Workers:")
        for worker in workers:
            print("* %s" % worker)


def handle_maintenance(proxy, options):
    proxy.scheduler.workers.update(options.hostname, None, "MAINTENANCE")

    if options.force or options.wait:
        worker_devices = proxy.scheduler.workers.show(options.hostname)["devices"]
        for device in proxy.scheduler.devices.list():
            if device["hostname"] not in worker_devices:
                continue
            current_job = device["current_job"]
            if current_job is not None:
                print("-> waiting for job %s" % current_job)
                # if --force is passed, cancel the job
                if options.force:
                    print("--> canceling")
                    proxy.scheduler.jobs.cancel(current_job)
                while options.wait and proxy.scheduler.jobs.show(current_job)["state"] != "Finished":
                    print("--> waiting")
                    time.sleep(5)


def handle_show(proxy, options):
    worker = proxy.scheduler.workers.show(options.hostname)
    if options.output_format == "yaml":
        print(yaml.dump(worker).rstrip("\n"))
    else:
        print("hostname    : %s" % worker["hostname"])
        print("description : %s" % worker["description"])
        print("state       : %s" % worker["state"])
        print("health      : %s" % worker["health"])
        print("devices     : %s" % ", ".join(worker["devices"]))
        print("last ping   : %s" % worker["last_ping"])


def handle_update(proxy, options):
    proxy.scheduler.workers.update(options.hostname,
                                   options.description,
                                   options.health)


def handle(proxy, options, _):
    handlers = {
        "add": handle_add,
        "config": handle_config,
        "list": handle_list,
        "maintenance": handle_maintenance,
        "show": handle_show,
        "update": handle_update
    }
    return handlers[options.sub_sub_command](proxy, options)
