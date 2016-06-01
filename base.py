
import re
import json
import os
from pprint import pprint
from datetime import datetime


def get_gspread_client():

    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials/google.json', scope)
    return gspread.authorize(credentials)


def get_worksheet(title, sheet):

    return get_gspread_client().open(title).worksheet(sheet)


def get_jenkins():

    from jenkinsapi.jenkins import Jenkins

    with open('credentials/jenkins.json') as data_file:
        jen_cred = json.load(data_file)

    jenkins = Jenkins('http://jenkins2.datastax.lan:8080/', username=jen_cred["username"], password=jen_cred["password"])
    return jenkins


def load_config(json_file):
    """
    Loads a report configuration from a .json file
    If the path is not absolute:
        - the file is assumed to be in the "configurations" folder
        - the ".json" is optional
    """

    if not os.path.isabs(json_file):
        if not json_file.endswith(".json"):
            json_file = "{0}.json".format(json_file)
        json_file = "configurations/{0}".format(json_file)

    if not os.path.exists(json_file):
        raise Exception("could not find json file: {0}".format(json_file))

    with open(json_file) as jf:
        return json.load(jf)


def duration(secs):

    r = ""
    if secs // (60 * 60) > 0:
        r += "{0}h".format(secs // (60 * 60))
        secs %= (60 * 60)
    if secs // 60 > 0:
        r += "{0}m".format(secs // (60))
        secs %= (60)
    if secs > 0 or len(r) == 0:
        r += "{0}s".format(secs)
    return r


def make_link(title, url):

    return '=HYPERLINK("{url}", "{title}")'.format(title=title, url=url)


def find_dicts(list, key, value=None):
    """
    The Jenkins API has many lists of dicts. This is a utility for extracting dicts.
    """
    return [x for x in list if key in x and (value == None or x[key] == value)]


def get_build_parameters(build):

    for x in build._data['actions']:
        if 'parameters' in x:
            return {y["name"]: y["value"] for y in x["parameters"]}
    return None


def compare(bps, config_bps):

    for k, v in config_bps.iteritems():
        if k not in bps or bps[k] != v:
            return False
    return True


def combine(config, build_spec):

    base = dict(config["base"]) if "base" in config else {}
    base.update(build_spec)
    return base


def find_build(job, config, build_spec, max_attempts=50):

    base = combine(config, build_spec)
    print "build spec:", base

    if "build" in base:
        return job.get_build(base["build"])

    version = base["version"]
    last = job.get_last_buildnumber()
    print job.name, last, base, version

    for i in range(last, max(0, last - max_attempts), -1):
        b = job.get_build_metadata(i)
        bps = get_build_parameters(b)
        print i, bps
        if "bps" in base and not compare(bps, base["bps"]):
            continue
        if bps["DSE_VERSION"] == version:
            return job.get_build(i)


def get_triggered_builds(build):

    jobs = []
    urls = [x['url'] for x in build.get_actions()['triggeredBuilds']]

    for url in urls:
        m = re.search(r"/job/([^/]+)/(\d+)/", url)
        if m:
            print "found: ", m.groups()
            jobs.append(m.groups())

    return jobs


class WorksheetWriter:
    def __init__(self, config):
        wks = get_worksheet(config['drive_file'], config['sheet'])
        wks.resize(rows=1)
        self.worksheet = wks
    def write(self, row):
        self.worksheet.append_row(row)


class ConsoleWriter:
    def __init__(self, config):
        pass
    def write(self, row):
        print row


COLUMN_CREATOR = {
    "jobname": (lambda b: make_link(b.job.name, b.job.baseurl)),
    "buildno": (lambda b: make_link(b.buildno, b.baseurl)),
    "status": (lambda b: b._data['result']),
    "duration": (lambda b: duration(int(b.get_duration().total_seconds()))),
    "timestamp": (lambda b: b.get_timestamp().strftime("%B %e, %Y @ %R"))
}


def create_row(build, columns=None):

    columns = columns or ["jobname", "buildno", "status", "duration", "timestamp"]
    return [COLUMN_CREATOR[c](build) for c in columns]
