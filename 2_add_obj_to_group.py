
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

#Create hosts
batch = {}
batch['objects'] = []

batch_hosts = {}
batch_hosts['type'] = 'host'
batch_hosts['list'] = []
ips_to_create = ['10.0.4.1']
for ip in ips_to_create:
    data = {}
    data['name'] = f"host_{ip}"
    data['ip-address'] = ip
    batch_hosts['list'].append(data)
batch['objects'].append(batch_hosts)

#resp = apiCall.send_command('add-objects-batch', data=batch)
#apiCall.publish()


# Populate groups
group = {}
group['name'] = 'SOURCE_GROUP1'
group['members'] = {'add': ['host_10.0.4.1']}
#apiCall.send_command('set-group', data=group)

resp = apiCall.send_command('show-changes', data={})
print(resp)
#resp = apiCall.watch_task(json.loads(resp)['task-id'])
#print(resp['tasks'][0]['task-details'][0])


apiCall.logout()
