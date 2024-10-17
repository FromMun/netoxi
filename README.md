# NetOxi

NetOxi is a small script designed to link together Netbox and Oxidized.

If you are using CSV for router.db and want to have backups scheduled automatically for selected devices, this tool is for you.

Feature highlights:

Easy to setup. NetOxi does not need major changes to current instances of Netbox or Oxidized.
Base64 supported. NetOxi supports Base64 hashes as input for credentials.
Customizable. With NetOxi you can match your router.db format.
Debugable. With ```Debug == True```, NetOxi would write logs to file for simple troubleshooting.

# Workflow with NetOxi

- Network admin adds device to Netbox adding all necessary custom tags (see below).
- NetOxi wakes up by crontab (for instance every 30 mins sync).
- NetOxi gets all of devices with tag "oxidized-pool" that want to be backed up.
- NetOxi gets for each device in a pool folllowing: IP for managment, what OS it is using, does it use AD.
- If device is using AD for authentication:
1) Construct new router.db line with correct formating and write it to routers.txt.
2) Do it for all applicable devices.
3) Grab all lines in manual.txt, combine it with routers.txt write to routers.db.
4) Delete routers.txt

- If device is not using AD for authentication:
1) Write line to NetOxi_logs.txt "Device is not using AD".
2) Go to next device.

- Reload routers.db for Oxidized

# Dependecies

NetOxi assumes that you are using Active Directory to authenticate into your network devices, if you are using something else use common username instead.

NetOxi is written in Python, so you would need Python installed on your OS
[Install Python now](https://www.python.org/downloads/).

After Python is installed, NetOxi would need few libraries installed:

```
pip install logging base64
```

# Installation

Clone github repo to your Oxidized router.db location:

```
git clone https://github.com/FromMun/netoxi.git
```

Preparing NetBox:

NetOxi is using Netbox API and custom fields in order to retrieve information about nodes.

Firstly, create custom tag for devices that you want to backup. NetOxi is searching devices with that tag to parse through. It can be anything, but by default it is ```oxidized-pool'''

After that, NetOxi needs few custom fields: [SSH_IP], [OS] and [AD_Authentication]. Name of these tags is not customizable yet.

- [SSH_IP] - IP in this field would be used to populate router.db. 
- [OS] - Value of this field is used to determine OS used by network device, has to much models in Oxidized. Use text as type
- [AD_Authentication] - Boolean field that determines if device is using AD for authentication. True/False

Create API Token in Netbox, it would be used to authentiacate NetOxi. 

Edit netoxi.py with your favourite text editor and change editable part to macth your enviroment.

```
nano netoxi.py
```

Lastly make a crontab to envoke NetOxi on periodic base. It is recommended to use crontab under same user as oxidized.
For example every 30 minutes:

```
crontab -e 

30 * * * * python3 netoxi.py
```

# Debug

With ```DEBUG=True``` NetOxi would create logs and paste them into NetOxi_logs.txt. NetOxi would aslo leave routers.txt and would not delete it, that way you can see what devices NetOxi is getting.

By default NetOxi uses ```DEBUG=False``` and does not create logs and deletes routers.txt after it is done.

# Planned features

- Customizable [SSH_IP], [OS], [AD_Authentication] fields.
- More oxidized router.db map schemas. 
- Better documentation, with screenshots!
