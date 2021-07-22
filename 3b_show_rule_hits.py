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
mgmt_params['domain'] = 'CMA_1'
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
req_data = {}
req_data['rule-number'] = 1
req_data['layer'] = "Standard_VS2 Network"
req_data['show-hits'] = True
response = apiCall.send_command('show-access-rule', data=req_data)
print(response)
apiCall.logout()
