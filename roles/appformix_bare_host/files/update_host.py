#! /usr/bin/env python
import requests
import json
import sys
import time

auth_token = sys.argv[1]
auth_type = sys.argv[2]
post_url = sys.argv[3]
name = sys.argv[4]
task_url = sys.argv[5]
jti_inband_ip = sys.argv[6]

async_iterations = 60
async_wait = 1


def poll_for_task_state(base_url, task_id):
    header = {'content-type': 'application/json'}
    task_state_endpoint = base_url + task_id + '/state'
    for iteration in xrange(async_iterations):
        try:
            resp = requests.get(url=task_state_endpoint,
                                headers=header)
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

put_url = post_url + '/' + server_id
HEADERS = {'content-type': 'application/json'}
HEADERS['X-Auth-Token'] = auth_token
HEADERS['X-Auth-Type'] = auth_type

data = {'MetaData': {'JtiInBandIp': jti_inband_ip}}
data = json.dumps(data)
result = requests.put(url=put_url, headers=HEADERS, data=data)
if result.status_code != 200:
    raise Exception('Put failed to url={0}, data={1}, error={2}'.
                    format(put_url, data, result.text))
task_id = json.loads(result.text).get('task_id')
task_state = poll_for_task_state(task_url, task_id)
if task_state != 'SUCCESS':
    raise Exception('Task {0} failed with state {1}'.
                    format(task_id, task_state))
