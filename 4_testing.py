import os
import ipaddress
import time
import json
from packages.simplecpapi import CPAPI # 

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
mgmt_params['domain']  = 'CMA_4'
# You only need username + password, OR API key - not both.
# If you provide both - only the API key will be used
if 'MGMT_API_KEY' in os.environ:
    mgmt_params['api-key'] = os.environ['MGMT_API_KEY']
elif 'MGMT_USERNAME' and 'MGMT_PASSWORD' in os.environ:
    mgmt_params['username'] = os.environ['MGMT_USERNAME']
    mgmt_params['password'] = os.environ['MGMT_PASSWORD']
else:
    print("[ERROR] Missing credentials MGMT_IP, MGMT_API_KEY or MGMT_USERNAME and MGMT_PASSWORD")
    raise SystemExit

apiCall = CPAPI(mgmt_params)

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

obj_prefix = "dbtobj_"
resp = tidy_up_hosts(obj_prefix, apiCall)
print(resp)