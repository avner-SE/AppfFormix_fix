#! /usr/bin/env python
import requests
import json
import sys
import time

auth_token = sys.argv[1]
auth_type = sys.argv[2]
name = sys.argv[3]
host_ip = sys.argv[4]
post_url = sys.argv[5]
source = sys.argv[6]
task_url = sys.argv[7]
automatic_instance_discovery = sys.argv[8]
try:
    aggr_id = sys.argv[9]
except Exception:
    aggr_id = None
async_iterations = 20
async_wait = 1

CERT_VERIFY_FLAG = False


def poll_for_task_state(base_url, task_id):
    header = {'content-type': 'application/json'}
    task_state_endpoint = base_url + task_id + '/state'
    for iteration in xrange(async_iterations):
        try:
            resp = requests.get(url=task_state_endpoint,
                                headers=header, verify=CERT_VERIFY_FLAG)
        except Exception as e:
            time.sleep(async_wait)
            continue
        task_state = json.loads(resp.text)
        if ('PENDING' == task_state):
            # Task is still running. Wait and check again
            time.sleep(async_wait)
        elif ('SUCCESS' == task_state):
            return task_state
        else:
            return task_state
    return task_state


# Use a unique ID namespace for bare hosts configured by Ansible role
server_id = 'ansible_bare_host__' + name.replace('.', '_')

get_url = post_url + '/' + server_id
HEADERS = {'content-type': 'application/json'}
link_capacity = '10G'
HEADERS['X-Auth-Token'] = auth_token
HEADERS['X-Auth-Type'] = auth_type

response = requests.get(url=get_url, headers=HEADERS, verify=CERT_VERIFY_FLAG)
# The same bare host might be posted multiple times because
# it may be playing multiple roles in a hyperconverged infrastructure.
# So we allow Ansible to post the bare host and server crud handles it.
if response.status_code in [404, 200]:
    base_url = 'http://' + host_ip + ':42595'
    if str(automatic_instance_discovery).lower() == 'false':
        automatic_instance_discovery = False
    else:
        automatic_instance_discovery = True
    data = {"Name": name, "HostName": host_ip,
            "LinkCapacity": link_capacity,
            "ServerId": server_id, "Source": source,
            "AgentBaseUrl": base_url,
            "AutomaticInstanceDiscovery": automatic_instance_discovery,
            }
    if aggr_id:
        data.update({"MetaData": {"AggregateId": aggr_id }})
    data = json.dumps(data)
    result = requests.post(url=post_url, headers=HEADERS, data=data,
                           verify=CERT_VERIFY_FLAG)
    if result.status_code != 200:
        raise Exception('Post failed to url={0}, data={1}, error={2}'.
                        format(post_url, data, result.text))
    task_id = json.loads(result.text).get('task_id')
    task_state = poll_for_task_state(task_url, task_id)
    if task_state != 'SUCCESS':
        raise Exception('Task {0} failed with state {1}'.
                        format(task_id, task_state))
else:
    data = json.loads(response.text)
    raise Exception('Get failed to url={0}, error={1}'.
                    format(get_url, data['message']))
