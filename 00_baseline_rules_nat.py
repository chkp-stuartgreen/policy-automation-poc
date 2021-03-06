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
  hosts_to_create = 2000
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

def create_rules(apiobj, obj_prefix, layer_name):
  # Create rules - keeping the logic for creating the hosts to generate the names for rule objects
  # apiCall = CPAPI(mgmt_params) # new session
  starting_address = "10.129.0.1"
  rules_to_create = 2000 # Needs to match how many objects you created
  ip_starting_address = ipaddress.IPv4Address(starting_address)
  
  for i in range(rules_to_create):
    ruleDetails = {}
    ruleDetails['layer'] = layer_name
    ruleDetails['name'] = obj_prefix
    ruleDetails['position'] = {}
    ruleDetails['position']['bottom'] = 'Bulk'
    ruleDetails['action'] = 'Accept'
    ruleDetails['source'] = obj_prefix + \
      str(ipaddress.IPv4Address(int(ip_starting_address + i)))
    ruleDetails['service'] = 'http'
    apiobj.send_command('add-access-rule', data=ruleDetails)

    if i % 100 == 0:
      print("[INFO] Publishing batch of 100 rules")
      resp = apiobj.publish()
      print(resp)

  test = apiobj.publish()
  print(test)

def create_nat_rules(apiobj, obj_prefix, package_name):
  mgmt_pkg = package_name
  # Create rules - keeping the logic for creating the hosts to generate the names for rule objects
  # apiCall = CPAPI(mgmt_params) # new session
  starting_address = "10.129.0.1"
  rules_to_create = 1500 # Needs to match how many objects you created
  ip_starting_address = ipaddress.IPv4Address(starting_address)
  
  for i in range(rules_to_create):
    ruleDetails = {}
    ruleDetails['package'] = mgmt_pkg # Only one NAT layer / rulebase per package
    ruleDetails['name'] = obj_prefix
    ruleDetails['position'] = {}
    ruleDetails['position']['bottom'] = 'Bulk'
    ruleDetails['original-source'] = obj_prefix + \
      str(ipaddress.IPv4Address(int(ip_starting_address + i)))
    ruleDetails['original-service'] = 'http'
    apiobj.send_command('add-nat-rule', data=ruleDetails)

    if i % 100 == 0:
      print("[INFO] Publishing batch of 100 rules")
      resp = apiobj.publish()
      print(resp)

  test = apiobj.publish()
  print(test)

def delete_access_rules(apiobj, obj_prefix, layer_name):
  batch_size = 500 # maximum size is 500
  offset = 0
  rule_uids_to_delete = []
  req_params = {}
  req_params['name'] = layer_name
  req_params['offset'] = offset
  req_params['limit'] = batch_size # max is 500 - but will affect performance
  rules = json.loads(apiobj.send_command('show-access-rulebase', data=req_params))
  #filtered_rules_1 = [i for i in rules['rulebase'] if i['name'] == 'Bulk'][0]['rulebase']
  #filtered_rules_2 = [i['uid'] for i in filtered_rules_1 if i['name'] == obj_prefix]
  while 'to' in rules:
    filtered_rules_1 = [i for i in rules['rulebase'] if i['name'] == 'Bulk'][0]['rulebase']
    filtered_rules_2 = [i['uid'] for i in filtered_rules_1 if i['name'] == obj_prefix]
    rule_uids_to_delete += filtered_rules_2
    req_params['offset'] += batch_size
    rules = json.loads(apiobj.send_command('show-access-rulebase', data=req_params))
  print(f"[INFO] Rules")
  #print(rule_uids_to_delete)
  for i,v in enumerate(rule_uids_to_delete):
    del_req_payload = {}
    del_req_payload['uid'] = v
    del_req_payload['layer'] = layer_name
    resp = apiobj.send_command('delete-access-rule', data=del_req_payload)
    #print(resp)
    if i % 100 == 0:
      apiobj.publish()
    # Get more objects and repeat the cycle
    #req_params = {}
    #req_params['name'] = layer_name
    #req_params['offset'] = 0
    #req_params['limit'] = 100 # max is 500 - but will affect performance
    #rules = json.loads(apiobj.send_command('show-access-rulebase', data=req_params))
    #filtered_rules_1 = [i for i in rules['rulebase'] if i['name'] == 'Bulk'][0]['rulebase']
    #filtered_rules_2 = [i['uid'] for i in filtered_rules_1 if i['name'] == obj_prefix]
  apiobj.publish()

def delete_nat_rules(apiobj, obj_prefix, package_name):
  batch_size = 500 # maximum size is 500
  offset = 0
  rule_uids = []
  rule_uids_to_delete = []
  req_params = {}
  req_params['package'] = package_name
  req_params['offset'] = offset
  req_params['limit'] = batch_size # max is 500 - but will affect performance
  rules = json.loads(apiobj.send_command('show-nat-rulebase', data=req_params))
  #filtered_rules_1 = [i for i in rules['rulebase'] if i['name'] == 'Bulk'][0]['rulebase']
  #filtered_rules_2 = [i['uid'] for i in filtered_rules_1 if i['name'] == obj_prefix]
  while 'to' in rules:
    filtered_rules_1 = [i for i in rules['rulebase'] if i['name'] == 'Bulk'][0]['rulebase']
    filtered_rules_2 = [i['uid'] for i in filtered_rules_1]
    rule_uids += filtered_rules_2
    req_params['offset'] += batch_size
    rules = json.loads(apiobj.send_command('show-nat-rulebase', data=req_params))
  # Extra step to retrieve name from show-nat-rule because rulebase doesn't have it
  for i,v in enumerate(rule_uids):
    req_params = {}
    req_params['package'] = package_name
    req_params['uid'] = v
    resp = json.loads(apiobj.send_command('show-nat-rule', data=req_params))
    if resp['name'] == obj_prefix:
      response = apiobj.send_command('delete-nat-rule', req_params)
      #print(response)
    if i % 100 == 0:
      apiobj.publish()
  apiobj.publish()



apiCall = CPAPI(mgmt_params)

# Uncomment each of these lines as required and then run with 
# python3 00_baseline_rules_nat.py
# Make sure you have the environment variables set for
# MGMT_API_KEY, MGMT_IP and DMS_DOMAIN

# Enable these rules to create 2000 hosts, 2000 firewall rules and 1500 NAT rules
# You must have a section in the access and NAT policies called "Bulk"
# or this will fail
# START SECTION #
#obj_prefix = str(uuid.uuid4()).split('-')[-1][-4:] + "_" # Create a random prefix to avoid conflicts, output for tidying later
#print(f'[INFO] Creating objects with a prefix of {obj_prefix}')
#print('[INFO] Make a note of this to tidy up the hosts / rules later')

#resp = batch_host_creation(apiCall, obj_prefix)
#resp = create_rules(apiCall, obj_prefix, 'Standard_VS1 Network')
#resp = create_nat_rules(apiCall, obj_prefix, 'Standard_VS1')
#print(f'[INFO] Finished - please check in SmartConsole')
#print(f'[INFO] FYI - object prefix is {obj_prefix} to save you scrolling back')
# END SECTION #


# These rules are if you need to use the API to delete the rules in the Bulk sections
# for performance or other reasons.
# You need to provide the access layer name for delete_access_rules and the rule / host prefix
# output with the previous command (or from the rulebase)
# START SECTION #

#resp = delete_access_rules(apiCall, '6079_', 'Standard_VS3 Network')
#resp = delete_nat_rules(apiCall, '6079_', 'Standard_VS3')
#resp = tidy_up_hosts(apiCall, '6079_')

# END SECTION #

apiCall.logout()