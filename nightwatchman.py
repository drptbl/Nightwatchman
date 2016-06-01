#!/usr/bin/env python

"""
Generates the following report:

--------------------------------------------------------------------
Generated on: 20160502 6:37 PM

QA_Weekly_Solr
QA_BdpMatrixSolr	     #337	SUCCESS	21m40s	  May  2, 2016 @ 14:41
...

QA_Weekly_Core
QA_BdpLeaseManager	      #62	SUCCESS	   12s	April 30, 2016 @ 22:23
...

NWM FINISHED
--------------------------------------------------------------------

"""

from base import *
import sys


class Context:
    def __init__(self):
        self.jenkins = None
        self.writer = None
        self.config = None
        self.create_row = None


def process_job(context, build_spec, job_name, build_number):

    build = context.jenkins.get_job(job_name).get_build(build_number)
    cells = context.create_row(build, columns=context.config.get("columns"))
    # print cells
    context.writer.write(cells)


def process_test(context, build_spec):

    parent_job = context.jenkins.get_job(build_spec['job'])
    build = find_build(parent_job, context.config, build_spec)
    print build.buildno

    jobs = get_triggered_builds(build)  # [(job name, build)...]
    print "found {0} jobs".format(len(jobs))

    header = [make_link("{0} #{1} ({2} jobs)".format(build_spec['job'], build.buildno, len(jobs)), build.baseurl)]
    context.writer.write(header)

    for i, j in enumerate(jobs):
        print "writing: ", i, j
        process_job(context, build_spec, j[0], int(j[1]))

    context.writer.write([""])


def generate_report(context):
    """
    @param config: Dict loaded from configuration JSON file
    """
    writer = context.config["writer"] if "writer" in context.config else "worksheet"
    context.writer = {"worksheet": WorksheetWriter, "console": ConsoleWriter}[writer](context.config)

    now = datetime.utcnow().strftime("%Y%m%d %-I:%M %p")
    context.writer.write(["Generated on: {0} UTC".format(now)])
    context.writer.write([""])

    for build_spec in context.config['jobs']:
        process_test(context, build_spec)

    context.writer.write(["NWM FINISHED"])


def main(args):

    if len(args) == 0:
        print "Usage: nightwatchman jsonfiles..."
        sys.exit(0)

    context = Context()
    context.jenkins = get_jenkins()
    context.create_row = create_row

    for a in args:
        context.config = load_config(a)
        generate_report(context)


if __name__ == "__main__":

    main(sys.argv[1:])

