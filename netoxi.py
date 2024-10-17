import requests
import json
import sys
import logging
import base64
import os

login_data = {'hostname': "host",'ssh_ip': "8.8.8.8",'ADUser': "user",'ADPwd': "pwd", 'net_os': 'ios'}     ###declaring dummy structure for map

###########################################################################################################################
##################Editable Part############################################################################################
                                                                                                                        

map_order = ['hostname', 'ssh_ip', 'net_os', 'ADUser', 'ADPwd']       ###change this for different order                ###
Encoded = False                                         ###do you want to encode credentials if no change to False      ###
NetboxToken = "NetboxToken"                             ###token to use for api                                         ###
NetboxUrl = "NetboxUrl"                                 ###what url to request and parse                                ###
PoolTag = "oxidized-pool"                               ###name of tag for devices in Oxidized pool                     ###
ADUser = "ADUser"                                       ###user for AD authentication                                   ###
ADPwd = "ADPwd"                                         ###password for AD authentication                               ###
reload_url = "http://127.0.0.1/reload"                  ###reload noads url, leave default if server is using port 80   ###
DEBUG = False                                           ###if True creates script logs                                  ###                                                                            

##################End of Editable Part#####################################################################################
###########################################################################################################################

if Encoded == False:
    NetboxToken = NetboxToken
    ADPwd = ADPwd
else:
    NetboxToken = base64.base64decode(NetboxToken)
    ADPwd = base64.base64decode(ADPwd)

open("routers.txt", "w").close() ### clear router.txt

if DEBUG == True:
    logging.basicConfig(filename="NetOxi_logs.txt",                 ###setting up logging
					    format='%(asctime)s %(message)s', 
					    filemode='w') 
    logger=logging.getLogger()                     
    logger.setLevel(logging.DEBUG)          ###level of debug

if DEBUG == True:
    logger.debug("Program Started")


head = {"Authorization": "token {}".format(NetboxToken)}        ###constructing headers

NetboxAPIUri =  NetboxUrl + "/api/dcim/devices/?tag=" + PoolTag

try:
    response_raw = requests.get(NetboxAPIUri, headers=head, verify=False)      ###constructing api request
    response_js = response_raw.json()   ###converting request to JSON
except requests.exceptions.ConnectionError:
    if DEBUG == True:
        logger.error("Connection error, check connection")
    sys.exit()
except requests.exceptions.Timeout:
    if DEBUG == True:
        logger.error("Connection Timeout")
    sys.exit()

response_count = response_js["count"]   ###count number of devices for loop 

for i in range(response_count):         ### parsing results
    login_data["hostname"] = response_js["results"][i]["display"]     ###grabing name of device
    login_data["ssh_ip"] = response_js["results"][i]["custom_fields"]["SSH_IP"]     ###grabing what ip to use for ssh 
    login_data["net_os"] = response_js["results"][i]["custom_fields"]["OS"]        ###grabing what os is running on device
    if response_js["results"][i]["custom_fields"]["AD_Authentication"] == True:         ### check if device is using AD ### 0 is a position of custom field, might need to change if pisition is off
        login_data["ADUser"] = ADUser
        login_data["ADPwd"] = ADPwd
        oxidized_db_line = ":".join(login_data[o] for o in map_order)     ###formating strig to oxidized format
        with open("routers.txt","a+") as file:       ###format line for oxidized and write it to file
            file.write(str(oxidized_db_line)+ "\n")
    else:
        if DEBUG == True:
            logger.info(login_data["hostname"] + " is using non AD authentication")        ###in case ad is not used, print message in console

data = data2 = "";              ###get data from manual entry file 
with open('manual.txt') as file:
    data = file.read()
with open('routers.txt') as file:     ###get data from automated file
    data2 = file.read()
 
data += "\n"        ###merging data
data += data2
 
with open ('router.db', 'w') as file:     ###finally write to router.db for oxi
    file.write(data)
    
try:
    response_raw = requests.get(reload_url)      ###reloading list of nodes   
except requests.exceptions.ConnectionError:
    if DEBUG == True:
        logger.error("Connection error when reloading list of nodes, check connection")
    sys.exit()
except requests.exceptions.Timeout:
    if DEBUG == True:
        logger.error("Connection Timeout when reloading list of nodes")
    sys.exit()

if DEBUG == True:
    logger.debug("Program Closed")

if DEBUG == False:
    os.remove("routers.txt")
sys.exit()
