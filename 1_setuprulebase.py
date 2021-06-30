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

# Create section headers
for i in reversed(range(3)):
    data = {}
    data['name'] = f"SectionTitle{i+1}"
    data['layer'] = 'Network'
    data['position'] = 'top'
    test = apiCall.send_command('add-access-section', data=data)
    print(test)
apiCall.publish()

#Create hosts
batch = {}
batch['objects'] = []

batch_hosts = {}
batch_hosts['type'] = 'host'
batch_hosts['list'] = []
ips_to_create = ['10.0.0.1', '10.0.2.1', '192.168.1.1']
for ip in ips_to_create:
    data = {}
    data['name'] = f"host_{ip}"
    data['ip-address'] = ip
    batch_hosts['list'].append(data)
batch['objects'].append(batch_hosts)

resp = apiCall.send_command('add-objects-batch', data=batch)
apiCall.publish()

# Create groups

host_group_names = ['SOURCE_GROUP1', 'DEST_GROUP1']
port_group_names = ['PORT_GROUP1']

for grp in host_group_names:
    data = {}
    data['name'] = grp
    apiCall.send_command('add-group', data)
apiCall.publish()

for grp in port_group_names:
    data = {}
    data['name'] = grp
    apiCall.send_command('add-service-group', data)
apiCall.publish()


# Populate groups
group = {}
group['name'] = 'SOURCE_GROUP1'
group['members'] = {'add': ['host_10.0.0.1', 'host_10.0.2.1']}
apiCall.send_command('set-group', data=group)
apiCall.publish()

group = {}
group['name'] = 'DEST_GROUP1'
group['members'] = {'add': ['host_192.168.1.1']}
apiCall.send_command('set-group', data=group)
apiCall.publish()

group = {}
group['name'] = 'PORT_GROUP1'
group['members'] = {'add': ['http']}
apiCall.send_command('set-service-group', data=group)
apiCall.publish()

# Create rule 1
rule = {}
rule['layer'] = 'Network'
rule['position'] = {}
rule['position']['top'] = "SectionTitle2"
rule['source'] = ['SOURCE_GROUP1']
rule['destination'] = ['DEST_GROUP1']
rule['service'] = ['PORT_GROUP1']
rule['action'] = 'accept'
rule['track'] = {'type': 'log'}
rule['name'] = "test rule 1"
rule['comments'] = "test comment"
resp = apiCall.send_command('add-access-rule', data=rule)
print(resp)
apiCall.publish()



apiCall.logout()
