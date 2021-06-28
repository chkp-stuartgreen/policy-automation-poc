import requests
import json
import urllib3
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CPAPI:
    def __init__(self, api_params):
        # Convert the MGMT parameters into a full URL to use elsewhere
        self.url = api_params['scheme'] + '://' + api_params['ip'] + ':' + api_params['port'] + \
            '/' + api_params['api_path'] + '/v' + api_params['api_ver'] + '/'
        # Create login headers to specify that the content type will be JSON
        login_headers = {
            'Content-Type': 'application/json'
        }

        # Create the payload for the HTTP POST request
        # Check for credentials - prefer API key if user and password methods are present too
        if 'api-key' in api_params and api_params['api-key'] != "":
            req_data = {}
            req_data['api-key'] = api_params['api-key']

        elif ('username' in api_params and 'password' in api_params) and (api_params['username'] != "" and api_params['password'] != ""):
            req_data = {}
            req_data['user'] = api_params['username']
            req_data['password'] = api_params['password']

        else:
            print("[ERROR] You didn't supply any credentials. Check you've added your API key or credentials as environment variables")
            raise SystemExit

        # format data as JSON for the HTTP POST body
        req_data = json.dumps(req_data)
        # Prepare an HTTP request and add the command 'login' to the command section of the URL
        response = requests.request(
            "POST", self.url + 'login', data=req_data, headers=login_headers, verify=False)

        # Check that the API replied with an HTTP 200 status code. If it did, we're good. Otherwise, we're not...
        if response.status_code == 200:
            sid = json.loads(response.text)['sid']
            self.auth_headers = {
                'Content-Type': 'application/json',
                'x-chkp-sid': sid
            }
        else:
            print("Error - could not connect to API. Non HTTP 200 status code received")
            raise SystemExit

    # Generic wrapper for sending commands to the API
    def send_command(self, command, data):
        response = requests.request("POST", self.url + command, data=json.dumps(data), headers=self.auth_headers,
                                    verify=False)
        # self.watch_task(json.loads(response.text)['task-id']) # This doesn't work yet - responses can have single task-ids or lists
        return response.text

    def watch_task(self, task_id):
        while True:
            task_details = json.loads(self.send_command(
                'show-task', data={'task-id': task_id}))
            if task_details['tasks'][0]['progress-percentage'] < 100:
                print(
                    f"[INFO] Waiting for task {task_id} to complete, {str(task_details['tasks'][0]['progress-percentage'])}%) complete")
                time.sleep(1)
            else:
                print("[INFO] Task completed")
                break

    def publish(self):  # Publish action
        data = {}
        cmd = 'publish'
        response = requests.request("POST", self.url + cmd, data=json.dumps(data), headers=self.auth_headers,
                                    verify=False)
        task_id = json.loads(response.text)['task-id']
        while True:
            task_details = json.loads(self.send_command(
                'show-task', data={'task-id': task_id}))
            if task_details['tasks'][0]['progress-percentage'] < 100:
                print("[INFO] Waiting for publish to complete, " +
                      str(task_details['tasks'][0]['progress-percentage']) + "% complete")
                time.sleep(3)
            else:
                print("[INFO] Publish completed")
                break
        return response.text

    def logout(self):  # Logout action
        cmd = 'logout'
        data = {}
        response = requests.request("POST", self.url + cmd, data=json.dumps(data), headers=self.auth_headers,
                                    verify=False)
        return response.text

if __name__ == "__main__":
  print("[ERROR] - You shouldn't be running this file directly! Instead - import it in another file")