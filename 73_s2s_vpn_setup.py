	
# Configure and verify both manually and by API:
# Route-based S2S VPN
# ESP tunnel mode
# IKE v2, Group 14
# Authentication: Shared secret / certificate
# Hashing/Encryption: AES-GCM/CCM-128+, SHA-256+ AES-CTR-128+ or SHA-128+ AES-CBC-128+

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
print("[WARNING] This script requires an interoperable device to be present and named vpn_peer_a")
input("[WARNING] Please verify and press enter to continue")
apiCall = CPAPI(mgmt_params)

# Create an empty group for the VPN domain to force route-based mode
group_name = "S2S_empty_group"
group = {}
group['name'] = group_name
apiCall.send_command('add-group', data= group)
apiCall.publish()

# Create dict for VPN community properties
vpn_props = {}
vpn_props['name'] = "S2S_test"
vpn_props['encryption-method'] = "ikev2 only"
vpn_props['encryption-suite'] = "custom"
vpn_props['gateways'] = "vpn_peer_a"
vpn_props['shared-secrets'] = {}
vpn_props['shared-secrets']['external-gateway'] = "vpn_peer_a"
vpn_props['shared-secrets']['shared-secret'] = "vpn12345678901234567" # 20 char minimum
vpn_props['ike-phase-1'] = {}
vpn_props['ike-phase-1']['encryption-algorithm'] = "aes-256"
vpn_props['ike-phase-1']['data-integrity'] = "sha256"
vpn_props['ike-phase-1']['diffie-hellman-group'] = "group-14"
vpn_props['ike-phase-2'] = {}
vpn_props['ike-phase-2']['encryption-algorithm'] = "aes-gcm-256"
vpn_props['ike-phase-2']['data-integrity'] = "sha256"
#vpn_props['ike-phase-2']['ike-p2-use-pfs'] = True
#vpn_props['ike-phase-2']['ike-p2-pfs-dh-grp'] = "group-14"
vpn_props['override-vpn-domains'] = {}
vpn_props['override-vpn-domains']['gateway'] = "vpn_peer_a"
vpn_props['override-vpn-domains']['vpn-domain'] = "S2S_empty_group"
resp = apiCall.send_command('add-vpn-community-meshed', data = vpn_props)
print(resp)
apiCall.publish()
apiCall.logout()
