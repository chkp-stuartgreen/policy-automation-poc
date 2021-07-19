import os
import ipaddress
import time
import json

from requests import api
from packages.simplecpapi import CPAPI # 
import uuid

# Environment setup

# Management IP and authentication should be provided as environment variables.
# Windows (Powershell) $Env:MGMT_IP = '1.2.3.4'
# Linux: export MGMT_IP='1.2.3.4' etc.

mgmt_params = {}
mgmt_params['port'] = '443'
mgmt_params['scheme'] = 'https'
mgmt_params['api_ver'] = '1.7'
mgmt_params['api_path'] = 'web_api'
mgmt_params['ip'] = os.environ['MGMT_IP']
mgmt_params['domain'] = os.environ['DMS_DOMAIN']
if 'MGMT_API_KEY' in os.environ:
    mgmt_params['api-key'] = os.environ['MGMT_API_KEY']
elif 'MGMT_USERNAME' and 'MGMT_PASSWORD' in os.environ:
    mgmt_params['username'] = os.environ['MGMT_USERNAME']
    mgmt_params['password'] = os.environ['MGMT_PASSWORD']
else:
    print("[ERROR] Missing credentials MGMT_IP, MGMT_API_KEY or MGMT_USERNAME and MGMT_PASSWORD")
    raise SystemExit

def batch_host_creation(apiobj, obj_prefix):
  # Object creation using the batch api (limited to 500 requests per batch)
  # For a batch delete example see the tidy_up_hosts function
  #apiCall = CPAPI(mgmt_params)
  starting_address = "10.129.0.1"
  hosts_to_create = 1500
  ip_starting_address = ipaddress.IPv4Address(starting_address)
  batch_dict = {}
  batch_objects = []
  type = {}
  type['type'] = 'host'
  list = []
  for i in range(hosts_to_create):
    hostDetails = {}
    hostDetails['name'] = obj_prefix + \
      str(ipaddress.IPv4Address(int(ip_starting_address + i)))
    hostDetails['ipv4-address'] = str(
      ipaddress.IPv4Address(int(ip_starting_address + i)))
    list.append(hostDetails)
    if i % 500 == 0:
      # publish if we have 500 in the list
      type['list'] = list
      batch_objects.append(type)
      batch_dict['objects'] = batch_objects
      resp = apiobj.send_command('add-objects-batch', data=batch_dict)
      resp = apiobj.publish()
      # reset object - not outer loop
      batch_dict = {}
      batch_objects = []
      type = {}
      type['type'] = 'host'
      list = []
  type['list'] = list
  batch_objects.append(type)
  batch_dict['objects'] = batch_objects
  resp = apiobj.send_command('add-objects-batch', data=batch_dict)
  resp = apiobj.publish()

def tidy_up_hosts(apiobj, obj_prefix):
  # Call this function with the object prefix and apiCall object to indiscriminately trash all of the hosts matching that pattern
  objfilter = {}
  objfilter['limit'] = 500  # max results - need to page / loop beyond this
  objfilter['in'] = ['name', obj_prefix]
  objfilter['type'] = 'host'
  objects = json.loads(apiobj.send_command('show-objects', data=objfilter))
  offset = 0
  while len(objects['objects']) > 0:
    list_to_delete = []
    for i in objects['objects']:
      obj = {}
      obj['uid'] = i['uid']
      list_to_delete.append(obj)
    del_obj_filter = {}
    del_obj_filter['objects'] = []
    del_obj_root = {}
    del_obj_root['type'] = 'host'
    del_obj_root['list'] = list_to_delete
    del_obj_filter['objects'].append(del_obj_root)
    resp = apiobj.send_command('delete-objects-batch', data=del_obj_filter)
    pub_results = apiobj.publish()
    print(pub_results)
    objfilter = {}
    objfilter['in'] = ['name', obj_prefix]
    objfilter['type'] = 'host'
    objects = json.loads(apiobj.send_command(
        'show-objects', data=objfilter))

obj_prefix = str(uuid.uuid4()).split('-')[-1][-4:] # Create a random prefix to avoid conflicts, output for tidying later
print(f'[INFO] Creating objects with a prefix of {obj_prefix}')
print('[INFO] Make a note of this to tidy up the hosts / rules later')

apiCall = CPAPI(mgmt_params)
#resp = batch_host_creation(apiCall, obj_prefix)
resp = tidy_up_hosts(apiCall, 'facf')

