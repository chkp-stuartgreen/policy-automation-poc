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
mgmt_params['domain'] = 'CMA_5'
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

#print(apiCall.session_id)
#print(apiCall.send_command('show-session', data={}))
#apiCall.publish()
#apiCall.logout()
#apiCall = CPAPI(mgmt_params)
#print(apiCall.send_command('show-sessions', data={'limit':5, 'view-published-sessions': True}))
#apiCall.logout
#exit()

# NOTE - this test requires a gateway object in order for policy validation to succeed. 
# Make sure there is a gateway object in the policy before proceeding

input("[WARNING] Please check the policy of CMA_5 contains a gateway object otherwise\
     policy validation will not occur. Check manually and press enter to continue...")

# Grab previous session ID for easier way to remove changes

resp = json.loads(apiCall.send_command('show-sessions', data={'limit': 1, 'offset': 0, 'view-published-sessions': 'true'}))
prev_session = resp['objects'][0]['uid']

# Create 10/8 network

network={}
network['name'] = 'net_10.0.0.0_8'
network['subnet'] = '10.0.0.0'
network['mask-length'] = '8'

resp = apiCall.send_command('add-network', data=network)


# Create rule 
rule = {}
rule['layer'] = 'Network'
rule['position'] = {}
rule['position']['top'] = "SectionTitle2"
rule['source'] = ['net_10.0.0.0_8']
rule['destination'] = ['DEST_GROUP1']
rule['service'] = ['PORT_GROUP1']
rule['action'] = 'drop'
rule['track'] = {'type': 'log'}
rule['name'] = "shadow rule 1"
rule['comments'] = "test comment"
resp = apiCall.send_command('add-access-rule', data=rule)
print(resp)
resp = apiCall.publish()
print(resp)

resp = apiCall.send_command('verify-policy', data={'policy-package': 'Standard'})
print(resp)
input("[INFO] Press enter to proceed with revert")
resp = apiCall.send_command('revert-to-revision', data={'to-session': prev_session})
print(resp)
print("[INFO] Policy reverted")
print("[INFO] Adding NAT to host_192.168.1.1 for 1.1.1.1")

host = {}
host['name'] = 'host_192.168.1.1'
nat_settings = {}
nat_settings['auto-rule'] = True
nat_settings['ip-address'] = '1.1.1.1'
nat_settings['method'] = 'static'
host['nat-settings'] = nat_settings

resp = apiCall.send_command('set-host', data=host)
print(resp)
resp = apiCall.publish()
print(resp)
apiCall.logout()
