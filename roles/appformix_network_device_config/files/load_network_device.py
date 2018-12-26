#! /usr/bin/env python
import json
import requests
import sys
import time


auth_token = sys.argv[1]
auth_type = sys.argv[2]
url = sys.argv[3]
network_device_file = sys.argv[4]
task_url = sys.argv[5]
HEADERS = {'content-type': 'application/json'}
HEADERS['X-Auth-Token'] = auth_token
HEADERS['X-Auth-Type'] = auth_type
async_iterations = 60
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
            raise Exception('Task {} failed with state {}'.
                            format(task_id, task_state))
    raise Exception('Task {} failed'.format(task_id))

def get_interface_id(name):
    return name.replace('.', '_').replace('$', '_')

def check_configured(url, device_id):
    r = requests.get(url=url+'/'+device_id, headers=HEADERS,
                     verify=CERT_VERIFY_FLAG)
    if r.status_code == 200:
        return True
    return False

def post_single_network_device(data):
    try:
        resp = requests.post(url=url, data=data,
                             headers=HEADERS, verify=CERT_VERIFY_FLAG)
        if resp.status_code != 200:
            print ('Post fail to network_device_definition {}: {}'.
                    format(url, resp.text))
        task_id = json.loads(resp.text).get('task_id')
        poll_for_task_state(task_url, task_id)
    except Exception as e:
        print 'Exception in post the network_device config {}'.format(e)
    print 'Successfully added Network Device'

def put_single_network_device(device_id, data):
    try:
        resp = requests.put(url=url + "/{0}".format(device_id), data=data,
                            headers=HEADERS, verify=CERT_VERIFY_FLAG)
        if resp.status_code != 200:
            print ('Put failed to network_device_definition {}: {}'.
                    format(url, resp.text))
        task_id = json.loads(resp.text).get('task_id')
        if task_id:
            poll_for_task_state(task_url, task_id)
    except Exception as e:
        print 'Exception in putting the network_device config {}'.format(e)
    print 'Successfully put Network Device - {}'.format(device_id)

try:
    with open(network_device_file) as config_file:
        data = json.loads(config_file.read())
except Exception as e:
    print 'Cannot parse network_device config file: {0}'.format(e)
    sys.exit(1)

network_device_list = data['NetworkDeviceList']

for entry in network_device_list:
    interface_list = []
    device = entry['NetworkDevice']
    device_id = device['NetworkDeviceId']
    source = device['Source']
    if type(source) != list:
        source = [source]
    config_data = \
        {'ChassisType': device['ChassisType'],
         'NetworkDeviceId': device_id,
         'Name': device['Name'],
         'NodeType': 'physical-router',
         'Description': "",
         "Source": source,
         "ManagementIp": device["ManagementIp"],
         'ConnectionInfo': device['ConnectionInfo'],
         'MetaData': device['MetaData']}
    if not device.get('InterfaceList'):
        for entry in config_data['ConnectionInfo']:
            entry['type'] = ''
            entry['local_interface_index'] = entry['local_interface_name']
            entry['remote_interface_index'] = entry['remote_interface_name']
            interface_obj = {'InterfaceName': entry['local_interface_name'],
                             'InterfaceId':
                             get_interface_id(entry['local_interface_name'])}
            interface_list.append(interface_obj)
    else:
        interface_list = device['InterfaceList']

    config_data['InterfaceList'] = interface_list
    json_data = json.dumps(config_data)
    if check_configured(url, device_id):
        put_single_network_device(device_id, json_data)
    else:
        post_single_network_device(json_data)
