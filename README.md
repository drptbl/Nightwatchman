# Nightwatchman

### About

A Jenkins-to-GoogleSheets report generator with a declarative style.

### Run

`python nightwatchman.py configurations...`  

Must be run from nightwatchman root folder.  
Configuration names must match file names in "configurations" folder.  
The ".json" extension is optional.

### Install Libraries

`sudo pip install gspread`    
`sudo pip install jenkinsapi`

### Setup

In the "credentials" folder, create "jenkins.json" from the template and populate it with a username and ldap password

Obtain the team's "google.json" credentials file or generate one yourself.
To generate one, follow the gspread instructions for creating a "service account key": http://gspread.readthedocs.org/en/latest/oauth2.html
Download that json file and save it as "google.json" in the "credentials" folder

### Configuration Files

Report configurations are in the JSON format.  

They support the following entries. They are all Strings except where noted.  

Config parameters:  
drive_file = the Google spreadsheet to write to  
sheet = the worksheet tab in the spreadsheet  
columns (list) = the cells to write for each row (supports: jobname, buildno, status, duration, timestamp)  
writer = the output writer (supports: spreadsheet, console)  
base (dict) = every test will inherit these parameters  
jobs (list of dicts) = the jobs to find. assumed to have kicked off other jobs. those jobs are printed as rows. View the job parameters below.  

Test parameters:  
job = the Jenkins job name  
version = the most recent version or branch to find  
bps (dict) = build parameters to filter by (ex. "bps": {"INSTALL_TYPE": "tar", "PROVIDER": "openstack"})  
build (int) = will grab this build number and will ignore version and bps  

### Sites

gspread  
https://github.com/burnash/gspread  
http://gspread.readthedocs.org/en/latest/index.html  

jenkinsapi  
https://github.com/salimfadhley/jenkinsapi  
https://jenkinsapi.readthedocs.org/en/latest/build.html  

