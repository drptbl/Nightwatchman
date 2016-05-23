# Nightwatchman

### Run

`python nightwatchman.py configuration...`  

Must be run from nightwatchman root folder.  
Configuration names must match file names in "configurations" folder.  
The ".json" extension is optional.

### Install Libraries

`sudo pip install gspread`    
`sudo pip install jenkinsapi`

### Setup

* Follow the gspread instructions for creating a "service account key" and downloading it as a json file: http://gspread.readthedocs.org/en/latest/oauth2.html
* Save that json file as "google.json" in the "credentials" folder
* Create "jenkins.json" in the "credentials" folder and populate it with a username and ldap password

### Sites

gspread  
https://github.com/burnash/gspread  
http://gspread.readthedocs.org/en/latest/index.html

jenkinsapi  
https://github.com/salimfadhley/jenkinsapi  
https://jenkinsapi.readthedocs.org/en/latest/build.html
