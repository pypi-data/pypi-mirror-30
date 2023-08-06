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
    devices_add = sub.add_parser("add", help="add a device")
    devices_add.add_argument("hostname", help="hostname of the device")
    devices_add.add_argument("--type", required=True, help="device-type")
    devices_add.add_argument("--worker", required=True, help="worker hostname")
    devices_add.add_argument("--description", default=None,
                             help="device description")

    owner = devices_add.add_mutually_exclusive_group()
    owner.add_argument("--user", default=None, help="device owner")
    owner.add_argument("--group", default=None, help="device group owner")

    devices_add.add_argument("--health", default=None,
                             choices=["GOOD", "UNKNOWN", "LOOPING", "BAD", "MAINTENANCE", "RETIRED"],
                             help="device health")

    devices_add.add_argument("--private", action="store_true", default=False,
                             help="private device, public by default")

    # "dict"
    devices_dict = sub.add_parser("dict", help="device dictionary")
    dict_sub = devices_dict.add_subparsers(dest="sub_sub_sub_command",
                                           help="Sub commands")
    dict_sub.required = True
    dict_get = dict_sub.add_parser("get",
                                   help="get the device dictionary")
    dict_get.add_argument("hostname", help="hostname of the device")
    dict_get.add_argument("--context", default=None,
                          help="job context for template rendering")
    dict_get.add_argument("--render", action="store_true", default=False,
                          help="render the dictionary into a configuration")

    dict_set = dict_sub.add_parser("set",
                                   help="set the device dictionary")
    dict_set.add_argument("hostname", help="hostname of the device")
    dict_set.add_argument("config", type=argparse.FileType('r'),
                          help="device dictionary file")

    # "list"
    devices_list = sub.add_parser("list", help="list available devices")
    devices_list.add_argument("--all", "-a", action="store_true",
                              default=False,
                              help="list every devices, inluding retired")
    devices_list.add_argument("--yaml", dest="output_format", default=None,
                              action="store_const", const="yaml",
                              help="print as yaml")

    # "maintenance"
    devices_maintenance = sub.add_parser("maintenance",
                                         help="maintenance the device")
    devices_maintenance.add_argument("hostname", help="device hostname")
    devices_maintenance.add_argument("--force", default=False,
                                     action="store_true",
                                     help="force device maintenance by canceling running job")
    devices_maintenance.add_argument("--no-wait", dest="wait",
                                     default=True, action="store_false",
                                     help="do not wait for the device to be idle")

    # "show"
    devices_show = sub.add_parser("show", help="show device details")
    devices_show.add_argument("hostname", help="device hostname")
    devices_show.add_argument("--yaml", dest="output_format",
                              action="store_const", const="yaml",
                              default=None, help="print as yaml")

    # "tags"
    devices_tags = sub.add_parser("tags", help="manage tags for the given device")
    tags_sub = devices_tags.add_subparsers(dest="sub_sub_sub_command",
                                           help="Sub commands")
    tags_sub.required = True
    tags_add = tags_sub.add_parser("add", help="add a tag")
    tags_add.add_argument("hostname", help="hostname of the device")
    tags_add.add_argument("tag", help="name of the tag")

    tags_list = tags_sub.add_parser("list", help="list tags for the device")
    tags_list.add_argument("hostname", help="hostname of the device")
    tags_list.add_argument("--yaml", dest="output_format",
                           action="store_const", const="yaml",
                           help="print as yaml")

    tags_del = tags_sub.add_parser("delete", help="remove a tag")
    tags_del.add_argument("hostname", help="hostname of the device")
    tags_del.add_argument("tag", help="name of the tag")

    # "update"
    devices_update = sub.add_parser("update", help="update device properties")
    devices_update.add_argument("hostname",
                                help="hostname of the device")
    devices_update.add_argument("--worker", default=None,
                                help="worker hostname")
    devices_update.add_argument("--description", default=None,
                                help="device description")

    owner = devices_update.add_mutually_exclusive_group()
    owner.add_argument("--user", default=None, help="device owner")
    owner.add_argument("--group", default=None, help="device group owner")

    devices_update.add_argument("--health", default=None,
                                choices=["GOOD", "UNKNOWN", "LOOPING", "BAD", "MAINTENANCE", "RETIRED"],
                                help="device health")

    display = devices_update.add_mutually_exclusive_group()
    display.add_argument("--public", default=None, action="store_true",
                         help="make the device public")
    display.add_argument("--private", dest="public", action="store_false",
                         help="make the device private")


def help_string():
    return "manage devices"


def handle_add(proxy, options):
    proxy.scheduler.devices.add(options.hostname, options.type,
                                options.worker, options.user,
                                options.group, not options.private,
                                options.health, options.description)


def handle_dict(proxy, options):
    if options.sub_sub_sub_command == "get":
        config = proxy.scheduler.devices.get_dictionary(options.hostname,
                                                        options.render,
                                                        options.context)
        print(str(config).rstrip("\n"))
    else:
        config = options.config.read()
        ret = proxy.scheduler.devices.set_dictionary(options.hostname,
                                                     config)
        if not ret:
            print("Unable to set the configuration")
        return 0 if ret else 1


def handle_list(proxy, options):
    devices = proxy.scheduler.devices.list(options.all)

    if options.output_format == "yaml":
        print(yaml.dump(devices).rstrip("\n"))
    else:
        print("Devices:")
        for device in devices:
            print("* %s (%s): %s,%s" % (device["hostname"], device["type"], device["state"], device["health"]))


def handle_maintenance(proxy, options):
    proxy.scheduler.devices.update(options.hostname, None, None, None, None,
                                   "MAINTENANCE", None)
    device = proxy.scheduler.devices.show(options.hostname)
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
    device = proxy.scheduler.devices.show(options.hostname)

    if options.output_format == "yaml":
        print(yaml.dump(device).rstrip("\n"))
    else:
        print("name        : %s" % device["hostname"])
        print("device-type : %s" % device["device_type"])
        print("state       : %s" % device["state"])
        print("health      : %s" % device["health"])
        print("user        : %s" % device["user"])
        print("group       : %s" % device["group"])
        print("health      : %s" % device["health"])
        print("health job  : %s" % device["health_job"])
        print("description : %s" % device["description"])
        print("public      : %s" % device["public"])
        print("pipeline    : %s" % device["pipeline"])
        print("device-dict : %s" % device["has_device_dict"])
        print("worker      : %s" % device["worker"])
        print("current job : %s" % device["current_job"])
        print("tags        : %s" % device["tags"])


def handle_tags(proxy, options):
    if options.sub_sub_sub_command == "add":
        proxy.scheduler.devices.tags.add(options.hostname, options.tag)
    elif options.sub_sub_sub_command == "delete":
        proxy.scheduler.devices.tags.delete(options.hostname, options.tag)
    else:
        tags = proxy.scheduler.devices.tags.list(options.hostname)
        if options.output_format == "yaml":
            print(yaml.dump(tags).rstrip("\n"))
        else:
            print("Tags:")
            for tag in tags:
                print("* %s" % tag)


def handle_update(proxy, options):
    proxy.scheduler.devices.update(options.hostname, options.worker,
                                   options.user, options.group,
                                   options.public, options.health,
                                   options.description)


def handle(proxy, options, _):
    handlers = {
        "add": handle_add,
        "dict": handle_dict,
        "list": handle_list,
        "maintenance": handle_maintenance,
        "show": handle_show,
        "tags": handle_tags,
        "update": handle_update
    }
    return handlers[options.sub_sub_command](proxy, options)
