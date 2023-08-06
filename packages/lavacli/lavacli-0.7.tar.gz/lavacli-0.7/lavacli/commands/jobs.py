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
import datetime
import sys
import time
import yaml

from lavacli.utils import print_u


def configure_parser(parser):
    sub = parser.add_subparsers(dest="sub_sub_command", help="Sub commands")
    sub.required = True

    # "cancel"
    jobs_cancel = sub.add_parser("cancel", help="cancel a job")
    jobs_cancel.add_argument("job_id", help="job id")

    jobs_definition = sub.add_parser("definition", help="job definition")
    jobs_definition.add_argument("job_id", help="job id")

    # "list"
    jobs_list = sub.add_parser("list", help="list jobs")
    jobs_list.add_argument("--start", type=int, default=0,
                           help="skip the N first jobs")
    jobs_list.add_argument("--limit", type=int, default=10,
                           help="limit to N jobs")
    jobs_list.add_argument("--yaml", dest="output_format", default=None,
                           action="store_const", const="yaml",
                           help="print as yaml")

    # "logs"
    jobs_logs = sub.add_parser("logs", help="get logs")
    jobs_logs.add_argument("job_id", help="job id")
    jobs_logs.add_argument("--no-follow", default=False, action="store_true",
                           help="do not keep polling until the end of the job")
    jobs_logs.add_argument("--filters", default=None, type=str,
                           help="comma seperated list of levels to show")
    jobs_logs.add_argument("--polling", default=5, type=int,
                           help="polling interval in seconds, 5s by default")
    jobs_logs.add_argument("--raw", default=False, action="store_true",
                           help="print raw logs")

    # "run"
    jobs_run = sub.add_parser("run", help="run the job")
    jobs_run.add_argument("definition", type=argparse.FileType('r'),
                          help="job definition")
    jobs_run.add_argument("--filters", default=None, type=str,
                          help="comma seperated list of levels to show")
    jobs_run.add_argument("--no-follow", default=False, action="store_true",
                          help="do not keep polling until the end of the job")
    jobs_run.add_argument("--polling", default=5, type=int,
                          help="polling interval in seconds, 5s by default")
    jobs_run.add_argument("--raw", default=False, action="store_true",
                          help="print raw logs")

    # "show"
    jobs_show = sub.add_parser("show", help="job details")
    jobs_show.add_argument("job_id", help="job id")
    jobs_show.add_argument("--yaml", dest="output_format",
                           action="store_const", const="yaml",
                           default=None, help="print as yaml")

    # "resubmit"
    jobs_resubmit = sub.add_parser("resubmit", help="resubmit a job")
    jobs_resubmit.add_argument("job_id", help="job id")
    jobs_resubmit.add_argument("--filters", default=None, type=str,
                               help="comma seperated list of levels to show")
    jobs_resubmit.add_argument("--follow", default=True, dest="no_follow",
                               action="store_false",
                               help="resubmit and poll for the logs")
    jobs_resubmit.add_argument("--polling", default=5, type=int,
                               help="polling interval in seconds, 5s by default")
    jobs_resubmit.add_argument("--raw", default=False, action="store_true",
                               help="print raw logs")

    # "submit"
    jobs_submit = sub.add_parser("submit", help="submit a new job")
    jobs_submit.add_argument("definition", type=argparse.FileType('r'),
                             help="job definition")


def help_string():
    return "manage jobs"


def handle_cancel(proxy, options):
    proxy.scheduler.jobs.cancel(options.job_id)


def handle_definition(proxy, options):
    print(proxy.scheduler.jobs.definition(options.job_id))


def handle_list(proxy, options):
    jobs = proxy.scheduler.jobs.list(options.start, options.limit)
    if options.output_format == "yaml":
        print(yaml.dump(jobs).rstrip("\n"))
    else:
        print("Jobs:")
        for job in jobs:
            print("* %s: %s,%s [%s] (%s)" % (job["id"], job["state"],
                                             job["health"], job["submitter"],
                                             job["description"]))


if sys.stdout.isatty():
    COLORS = {"exception": "\033[1;31m]",
              "error": "\033[1;31m",
              "warning": "\033[1;33m",
              "info": "\033[1;37m",
              "debug": "",
              "target": "\033[32m",
              "input": "\033[0;35m",
              "feedback": "\033[0;33m",
              "results": "\033[1;34m",
              "dt": "\033[1;30m",
              "end": "\033[0m"}
else:
    COLORS = {"exception": "",
              "error": "",
              "warning": "",
              "info": "",
              "debug": "",
              "target": "",
              "input": "",
              "feedback": "",
              "results": "",
              "dt": "",
              "end": ""}


def print_logs(logs, raw, filters):
    filters = [] if filters is None else filters.split(',')
    if raw:
        for line in logs:
            if filters and not line["lvl"] in filters:
                continue
            print_u("- " + yaml.dump(line, default_flow_style=True,
                                     default_style='"',
                                     width=10 ** 6,
                                     Dumper=yaml.CDumper)[:-1])
    else:
        for line in logs:
            timestamp = line["dt"].split(".")[0]
            level = line["lvl"]
            if filters and level not in filters:
                continue
            if isinstance(line["msg"], dict) and \
               "sending" in line["msg"].keys():
                level = "input"
                msg = str(line["msg"]["sending"])
            elif isinstance(line["msg"], bytes):
                msg = line["msg"].decode("utf-8", errors="replace")
            else:
                msg = str(line["msg"])
            msg = msg.rstrip("\n")

            print_u(COLORS["dt"] + timestamp + COLORS["end"] + " " +
                    COLORS[level] + msg + COLORS["end"])


def handle_logs(proxy, options):
    # Loop
    lines = 0
    while True:
        (finished, data) = proxy.scheduler.jobs.logs(options.job_id, lines)
        logs = yaml.load(str(data), Loader=yaml.CLoader)
        if logs:
            print_logs(logs, options.raw, options.filters)
            lines += len(logs)
        # Loop only if the job is not finished
        if finished or options.no_follow:
            break

        # Wait some time
        time.sleep(options.polling)

    if finished:
        details = proxy.scheduler.jobs.show(options.job_id)
        if details.get("failure_comment"):
            print_logs([{"dt": datetime.datetime.utcnow().isoformat(),
                         "lvl": "info",
                         "msg": "[lavacli] Failure comment: %s" % details["failure_comment"]}],
                       options.raw, options.filters)


def handle_resubmit(proxy, options):
    job_id = proxy.scheduler.jobs.resubmit(options.job_id)

    if options.no_follow:
        if isinstance(job_id, list):
            for job in job_id:
                print(job)
        else:
            print(job_id)

    else:
        print_logs([{"dt": datetime.datetime.utcnow().isoformat(),
                     "lvl": "info",
                     "msg": "[lavacli] Job %s submitted" % job_id}],
                   options.raw, options.filters)

        # Add the job_id to options for handle_logs
        # For multinode, print something and loop on all jobs
        if isinstance(job_id, list):
            for job in job_id:
                print_logs([{"dt": datetime.datetime.utcnow().isoformat(),
                             "lvl": "info",
                             "msg": "[lavacli] Seeing %s logs" % job}],
                           options.raw, options.filters)
                options.job_id = job
                handle_logs(proxy, options)
        else:
            options.job_id = job_id
            handle_logs(proxy, options)


def handle_run(proxy, options):
    job_id = proxy.scheduler.jobs.submit(options.definition.read())
    print_logs([{"dt": datetime.datetime.utcnow().isoformat(),
                 "lvl": "info",
                 "msg": "[lavacli] Job %s submitted" % job_id}],
               options.raw, options.filters)

    # Add the job_id to options for handle_logs
    # For multinode, print something and loop on all jobs
    if isinstance(job_id, list):
        for job in job_id:
            print_logs([{"dt": datetime.datetime.utcnow().isoformat(),
                         "lvl": "info",
                         "msg": "[lavacli] Seeing %s logs" % job}],
                       options.raw, options.filters)
            options.job_id = job
            handle_logs(proxy, options)
    else:
        options.job_id = job_id
        handle_logs(proxy, options)


def handle_show(proxy, options):
    job = proxy.scheduler.jobs.show(options.job_id)

    if options.output_format == "yaml":
        job["submit_time"] = job["submit_time"].value
        job["start_time"] = job["start_time"].value
        job["end_time"] = job["end_time"].value
        print(yaml.dump(job).rstrip("\n"))
    else:
        print("id          : %s" % job["id"])
        print("description : %s" % job["description"])
        print("submitter   : %s" % job["submitter"])
        print("device-type : %s" % job["device_type"])
        print("device      : %s" % job["device"])
        print("health-check: %s" % job["health_check"])
        print("state       : %s" % job["state"])
        print("Health      : %s" % job["health"])
        if job.get("failure_comment"):
            print("failure     : %s" % job["failure_comment"])
        print("pipeline    : %s" % job["pipeline"])
        print("tags        : %s" % str(job["tags"]))
        print("visibility  : %s" % job["visibility"])
        print("submit time : %s" % job["submit_time"])
        print("start time  : %s" % job["start_time"])
        print("end time    : %s" % job["end_time"])


def handle_submit(proxy, options):
    job_id = proxy.scheduler.jobs.submit(options.definition.read())
    if isinstance(job_id, list):
        for job in job_id:
            print(job)
    else:
        print(job_id)


def handle(proxy, options, _):
    handlers = {
        "cancel": handle_cancel,
        "definition": handle_definition,
        "list": handle_list,
        "logs": handle_logs,
        "resubmit": handle_resubmit,
        "run": handle_run,
        "show": handle_show,
        "submit": handle_submit
    }
    return handlers[options.sub_sub_command](proxy, options)
