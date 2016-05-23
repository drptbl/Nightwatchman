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


def create_row(build):

    return [
        make_link(build.job.name, build.job.baseurl),
        make_link(build.buildno, build.baseurl),
        build._data['result'],
        duration(int(build.get_duration().total_seconds())),
        build.get_timestamp().strftime("%B %e, %Y @ %R")
    ]


def process_job(wks, jenkins, job_name, build_number):

    build = jenkins.get_job(job_name).get_build(build_number)
    cells = create_row(build)
    print cells
    wks.append_row(cells)


def section_header(wks, job_name, build, jobs):

    link = make_link("{0} #{1} ({2} jobs)".format(job_name, build.buildno, len(jobs)), build.baseurl)
    print link
    wks.append_row([link])


def process_test(wks, jenkins, config, build_spec):

    parent_job = jenkins.get_job(build_spec['job'])
    version = config['versions'][0] if 'versions' in config else None
    build = find_build(parent_job, build_spec, version=version)
    print build.buildno

    jobs = get_triggered_builds(build)  # [(job name, build)...]
    print "found {0} jobs".format(len(jobs))

    section_header(wks, build_spec['job'], build, jobs)

    for i, j in enumerate(jobs):
        print "writing: ", i, j
        process_job(wks, jenkins, j[0], int(j[1]))

    wks.append_row([""])


def generate_report(jenkins, config):
    """
    @param config: Dict loaded from configuration JSON file
    """

    wks = get_worksheet(config['drive_file'], config['sheet'])
    wks.resize(rows=1)
    now = datetime.utcnow().strftime("%Y%m%d %-I:%M %p")
    wks.append_row(["Generated on: {0} UTC".format(now)])
    wks.append_row([""])

    for build_spec in config['tests']:
        process_test(wks, jenkins, config, build_spec)

    wks.append_row(["NWM FINISHED"])


def main(args):

    if len(args) == 0:
        print "Usage: nightwatchman jsonfiles..."
        sys.exit(0)

    jenkins = get_jenkins()

    for a in args:
        generate_report(jenkins, load_config(a))


if __name__ == "__main__":

    main(sys.argv[1:])

