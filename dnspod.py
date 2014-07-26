#!/usr/bin/env python
#-*- coding:utf-8 -*-
 
# please use python 3

import http.client, urllib
import socket
import time
import json
 
debug = 1
params = dict(
    login_email="",      # replace with your email
    login_password="",   # replace with your password
    format="json",
)
DDNS_URL = "dnsapi.cn"
my_domain_name = ""      # replace with your domain name
my_domain_id = None
my_record_name = "www"
my_record_id = None
my_record_line = None
current_ip = None
 
# update Dynamic DNS with IP
def update_ddns(ip, domain_id, record_id, record_line):
    print ("++++update DDNS")
    params.update(dict(
#            value=ip, 
            domain_id=domain_id, 
            record_id=record_id, 
            sub_domain="www", 
            record_line=record_line,
#            record_line=record_line.decode('utf-8').encode('gb2312'),
#            record_line="д╛хо",
#            record_line=l_record_line.decode('utf-8'),
        )
    )
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/json"}
    conn = http.client.HTTPSConnection(DDNS_URL)
    conn.request("POST", "/Record.Ddns", urllib.parse.urlencode(params), headers)
    
    response = conn.getresponse()
    data = response.read()
    conn.close()
    ret = json.loads(data.decode())
    print (data)
    return ret["status"]["code"]
    #return response.status == 200
 
def getip():
    sock = socket.create_connection(('ns1.dnspod.net', 6666))
    sock.settimeout(10)
    ip = sock.recv(16)
    sock.close()
    return ip

def getdomainid():
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/json"}
    conn = http.client.HTTPSConnection(DDNS_URL)
    conn.request("POST", "/Domain.List", urllib.parse.urlencode(params), headers)
    
    response = conn.getresponse()
    data = response.read()
    if debug:
        print (data)
    conn.close()
    ret = json.loads(data.decode())
    if ret["status"]["code"] == "1": # success
        for domain_entry in ret["domains"][:]:
            if domain_entry["name"] == my_domain_name:
                domain_id = domain_entry["id"]
    if debug:
        print (domain_id)

    return domain_id

def getrecordid():
    global my_record_id, my_record_line
    params.update(dict(domain_id=my_domain_id))
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/json"}
    conn = http.client.HTTPSConnection(DDNS_URL)
    conn.request("POST", "/Record.List", urllib.parse.urlencode(params), headers)
    
    response = conn.getresponse()
    if debug:
        print (response.status, response.reason)
    data = response.read()
    if debug:
        print (data)
    conn.close()
    ret = json.loads(data.decode())
    if ret["status"]["code"] == "1": # success
        for record_entry in ret["records"][:]:
            if record_entry["name"] == my_record_name:
                my_record_id = record_entry["id"]
                my_record_line = record_entry["line"]
    if debug:
        print (my_record_id, my_record_line)

    return my_record_id
 
def getrecordline():
    params.update(dict(domain_id=my_domain_id, record_id=my_record_id))
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/json"}
    conn = http.client.HTTPSConnection(DDNS_URL)
    conn.request("POST", "/Record.Info", urllib.parse.urlencode(params), headers)
    
    response = conn.getresponse()
    if debug:
        print (response.status, response.reason)
    data = response.read()
    if debug:
        print (data)
    conn.close()
    ret = json.loads(data.decode())
    if ret["status"]["code"] == "1": # success
        for record_entry in ret["record"][:]:
            if record_entry["id"] == my_record_id:
                record_line = record_entry["record_line"]
    if debug:
        print (record_line)

    return record_id
 
if __name__ == '__main__':
    if my_domain_id == None:
        my_domain_id = getdomainid()
    if my_record_id == None:
        getrecordid()
#        my_record_id = getrecordid()
#    if my_record_line == None:
#        my_record_line = getrecordline()
    while True:
        try:
            ip = getip()
            print (ip)
            if current_ip != ip:
                if update_ddns(ip, my_domain_id, my_record_id, my_record_line):
                    current_ip = ip
        except:
            print (e)
            pass
        time.sleep(30)
