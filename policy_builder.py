import os
import ipaddress
import time
import json
from packages.simplecpapi import CPAPI # 


# A few helper functions for batch creation of hosts, rules and then tidy up

def tidy_up_hosts(prefix, apiobj):
    # Call this function with the object prefix and apiCall object to indiscriminately trash all of the hosts matching that pattern
    objfilter = {}
    objfilter['limit'] = 500  # max results - need to page / loop beyond this
    objfilter['in'] = ['name', prefix]
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
        apiobj.watch_task(json.loads(resp)['task-id'])
        pub_results = apiobj.publish()
        print(pub_results)
        objfilter = {}
        objfilter['in'] = ['name', prefix]
        objfilter['type'] = 'host'
        objects = json.loads(apiobj.send_command(
            'show-objects', data=objfilter))

def create_batch_hosts(apiobj):
    starting_address = "10.100.0.1"
    hosts_to_create = 10000

    ip_starting_address = ipaddress.IPv4Address(starting_address)
    start_time = time.perf_counter()
    print("Starting creation: " + str(start_time))
    for i in range(hosts_to_create):
        hostDetails = {}
        hostDetails['name'] = obj_prefix + \
            str(ipaddress.IPv4Address(int(ip_starting_address + i)))
        hostDetails['ipv4-address'] = str(
            ipaddress.IPv4Address(int(ip_starting_address + i)))
        if i < 2000:  # Add nat properties for the first 2000 hosts
            hostDetails['nat-settings'] = {}
            hostDetails['nat-settings']['auto-rule'] = True
            hostDetails['nat-settings']['method'] = 'hide'
            hostDetails['nat-settings']['hide-behind'] = 'gateway'
        apiobj.send_command('add-host', data=hostDetails)
        if i % 100 == 0:
            print("[INFO] Publishing batch of 500 hosts")
            # don't batch everything up - this makes mgmt sad.
            apiobj.publish()

    apiobj.publish()

def create_batch_rules(apiobj):
    # Create rules - keeping the logic for creating the hosts to generate the names for rule objects
    # apiCall = CPAPI(mgmt_params) # new session
    starting_address = "10.100.0.1"
    hosts_to_create = 10000
    ip_starting_address = ipaddress.IPv4Address(starting_address)
    start_time = time.perf_counter()
    print("Starting rule creation: " + str(start_time))
    for i in range(hosts_to_create):
        ruleDetails = {}
        ruleDetails['layer'] = 'Network'
        ruleDetails['position'] = 'bottom'
        ruleDetails['action'] = 'Accept'
        ruleDetails['source'] = obj_prefix + \
            str(ipaddress.IPv4Address(int(ip_starting_address + i)))
        ruleDetails['service'] = 'http'

        apiobj.send_command('add-access-rule', data=ruleDetails)
        if i % 100 == 0:
            print("[INFO] Publishing batch of 500 rules")
            apiobj.publish()

    test = apiobj.publish()

def batch_host_creation(apiobj):

    # Object creation using the batch api (limited to 500 requests per batch)
    # For a batch delete example see the tidy_up_hosts function
    #apiCall = CPAPI(mgmt_params)

    obj_prefix = "batch_"

    # Try out the batch create and see what happens...
    starting_address = "10.129.0.1"
    hosts_to_create = 500
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
        if i < 2000:  # Add nat properties for the first 2000 hosts
            hostDetails['nat-settings'] = {}
            hostDetails['nat-settings']['auto-rule'] = True
            hostDetails['nat-settings']['method'] = 'hide'
            hostDetails['nat-settings']['hide-behind'] = 'gateway'
        list.append(hostDetails)
    type['list'] = list
    batch_objects.append(type)
    batch_dict['objects'] = batch_objects

    resp = apiobj.send_command('add-objects-batch', data=batch_dict)
    print(resp)
    apiobj.watch_task(json.loads(resp)['task-id'])
    resp = apiobj.publish()
    print(resp)
    # end batch creation

# End helper functions


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
# You only need username + password, OR API key - not both.
# If you provide both - only the API key will be used
if os.environ['MGMT_API_KEY']:
    mgmt_params['api-key'] = os.environ['MGMT_API_KEY']
elif os.environ['MGMT_USERNAME'] and os.environ['MGMT_PASSWORD']:
    mgmt_params['username'] = os.environ['MGMT_USERNAME']
    mgmt_params['password'] = os.environ['MGMT_PASSWORD']
else:
    print("[ERROR] Missing credentials MGMT_IP, MGMT_API_KEY or MGMT_USERNAME and MGMT_PASSWORD")
    raise SystemExit

apiCall = CPAPI(mgmt_params)
#obj_prefix = "dbp_"
#result = apiCall.send_command('show-objects', data={})
# print(result)
#create_batch_hosts(apiCall)
#input('Hosts complete - start on rules?')
#create_batch_rules(apiCall)

#tidy_up_hosts(obj_prefix, apiCall)
test = apiCall.send_command('show-objects', data={})
print(test)