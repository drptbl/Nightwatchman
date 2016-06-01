#!/usr/bin/env python

"""
Utility for pretty printing Build objects into a file.
Helpful for learning the jenkins api.
"""

import json
import pprint
import sys
from jenkinsapi.jenkins import Jenkins

if len(sys.argv) < 2:
    print "Usage: dump job [build]"
    sys.exit(0)

with open('credentials/jenkins.json') as data_file:
    jen_cred = json.load(data_file)

jenkins = Jenkins('http://jenkins2.datastax.lan:8080/', username=jen_cred["username"], password=jen_cred["password"])

JOB = sys.argv[1]
j = jenkins.get_job(JOB)

BUILD = int(sys.argv[2]) if len(sys.argv) == 3 else j.get_last_buildnumber()
b = j.get_build(BUILD)

with open("examples/{0}_{1}_metadata.txt".format(b.job.name, b.buildno), "w") as f:
    pprint.pprint(b._data, stream=f)
