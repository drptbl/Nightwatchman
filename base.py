
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

    return build._data['actions'][1]['parameters']


def find_build(job, build_spec, version=None, max_attempts=50):
    """
    Finds a build based on the specification in the json file.
    Expects "build" or "version", but not both.
    If neither is provided, this function's "version" kwarg will be set to the current value from the json's "versions" list.
    """

    if build_spec.get('build'):
        return job.get_build(build_spec.get('build'))

    if build_spec.get('version'):
        version = build_spec.get('version')

    if not version:
        raise Exception("finding a build requires a build number or a version")

    print job, build_spec, version

    last = job.get_last_buildnumber()
    for i in range(last, max(0, last - max_attempts), -1):
        b = job.get_build_metadata(i)
        ps = get_build_parameters(b)
        rs = find_dicts(ps, "name", value="DSE_VERSION")
        print i, rs, ps
        if len(rs) == 1 and rs[0]["value"] == version:
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

