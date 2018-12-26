#! /usr/bin/env python
import json
import sys
import importlib
import requests
from ansible.module_utils.basic import *


async_iterations = 60
async_wait = 1

CERT_VERIFY_FLAG = False
PLUGIN_TYPE_ID_MAP = {'JTI': 'jti_network_device',
                      'GRPC': 'grpc_network_device'}
PLUGIN_TYPE_FILE_NAME_MAP = \
    {'JTI': 'certified_plugins/jti_config_all_sensors.json',
     'GRPC': 'certified_plugins/grpc_config_all_sensors.json'}


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


def main():
    fields = {
        "config_file_name": {"required": True, "type": "str"},
        "current_path" :{"required": True, "type": "str"},
        "plugin_url": {"required": True, "type": "str" },
        "plugin_type": {"required": True, "type": "str" },
        "auth_type": {"default": "openstack", "type": "str"},
        "token": {"default": "Fake", "type": "str"},
        "task_url": {"required": True, "type": "str" }
    }
    ansible_module = AnsibleModule(argument_spec=fields)
    file_name = ansible_module.params['config_file_name'].replace('.py', '')
    task_url = ansible_module.params['task_url']
    current_path = ansible_module.params['current_path']
    plugin_url = ansible_module.params['plugin_url']

    sys.path.append(current_path)
    sys.path.append('./')
    module = importlib.import_module(file_name)

    sensor_name = module.SENSOR_NAME
    entity_type = module.ENTITY_TYPE
    collection = module.__name__ + "_collection"
    metric_map = module.METRIC_LIST
    tmp = {sensor_name: {'MetricMap': metric_map,
                         'Collection': collection,
                         'EntityType': entity_type,
                         'SensorType': 'normal',
                         'ConfigFile': file_name}}

    HEADERS = {
        'content-type': 'application/json',
        'X-Auth-Token': ansible_module.params['token'],
        'X-Auth-Type': ansible_module.params['auth_type'],
    }
    plugin_id = PLUGIN_TYPE_ID_MAP[ansible_module.params['plugin_type']]
    url = plugin_url + '/' + plugin_id
    r = requests.get(url=url, headers=HEADERS,
                     verify=CERT_VERIFY_FLAG)
    if r.status_code == 200:
        p = r.json()['Plugin']
    else:
        ansible_module.exit_json(changed=False, meta=data)

    data = p['Config']['SensorMap']
    data.update(tmp)
    data = {'SensorMap': data}
    # upate the certified plugin json file
    file_name = PLUGIN_TYPE_FILE_NAME_MAP[ansible_module.params['plugin_type']]
    with open(file_name, 'w') as outfile:
        del p['Config']['ObjectList']
        del p['SnmpOIDList']
        json.dump(p, outfile)
    json_data = json.dumps(data)
    r = requests.put(url=url, headers=HEADERS, data=json_data,
                     verify=CERT_VERIFY_FLAG)
    if r.status_code != 200:
        ansible_module.fail_json(
            msg='Unable to update plugin',
            meta={'plugin_id': plugin_id})
    task_id = json.loads(r.text).get('task_id')
    poll_for_task_state(task_url, task_id)


    ansible_module.exit_json(changed=True, meta=tmp)


if __name__ == '__main__':
    main()
