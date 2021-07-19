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
      apiobj.watch_task(json.loads(resp)['task-id'])
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
  apiobj.watch_task(json.loads(resp)['task-id'])
  resp = apiobj.publish()

obj_prefix = uuid.uuid4().split('-')[-1][-4:] # Create a random prefix to avoid conflicts, output for tidying later
print(f'[INFO] Creating objects with a prefix of {obj_prefix}')
print('[INFO] Make a note of this to tidy up the hosts / rules later')

apiCall = CPAPI(mgmt_params)
resp = batch_host_creation(apiCall, obj_prefix)
