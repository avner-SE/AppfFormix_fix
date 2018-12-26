#! /usr/bin/env python2

import requests
import json
import sys

from ansible.module_utils.basic import *

# Some Remote plugins such as jti_usage_plugin which need to configure the
# device may take long time to complete
async_iterations = 60
async_wait = 1

CERT_VERIFY_FLAG = False


# Check if plugin is already configured, and return its configuration.
def is_configured(url, plugin_id, headers={}):
    r = requests.get(url=url+'/'+plugin_id, headers=headers,
                     verify=CERT_VERIFY_FLAG)
    if r.status_code == 200:
        p = r.json()['Plugin']
        return True, p
    return False, None


def compare_subset(p1, p2):
    for key, value in p1.iteritems():
        # For plugin Json, we will have keys which has a dictionary as value,
        # we need to only compare the inner_dictionary which new_plugin has
        if type(value) == dict:
            for inner_key, inner_value in value.iteritems():
                if inner_value != p2.get(key, {}).get(inner_key):
                    return False
        elif value != p2.get(key):
            return False
    return True


def create_aggregate(module, plugin_id, aggr_id, aggr_url, headers):
    data = json.dumps({'Id': aggr_id,
                       'Name': aggr_id,
                       'Type': 'host',
                       'ObjectList': []})
    r = requests.post(url=aggr_url, data=data, headers=headers,
                      verify=CERT_VERIFY_FLAG)
    output = r.json()
    if r.status_code == 400 and 'already exists' in output['message']:
        return
    if r.status_code != 200:
        module.fail_json(msg='Could not create aggregate: {0}'.
                         format(output), meta={'plugin_id': plugin_id,
                                               'aggregate_id': aggr_id})


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
        "json_file": {"required": True, "type": "str"},
        "plugin_url": {"required": True, "type": "str" },
        "aggr_url": {"required": False, "type": "str" },
        "token": {"default": "Fake", "type": "str"},
        "aggregate_id": {"required": False, "type": "str"},
        "log_file_path": {"required": False, "type": "str"},
        "auth_type": {"default": "openstack", "type": "str"},
        "task_url": {"required": True, "type": "str" }
    }
    module = AnsibleModule(argument_spec=fields)

    plugin_url = module.params['plugin_url']
    aggr_url = module.params['aggr_url']
    filename = module.params['json_file']
    task_url = module.params['task_url']
    aggregate_id = module.params.get('aggregate_id', "")
    log_file_path = module.params.get('log_file_path', "")
    if log_file_path:
        log_file_path = log_file_path.split(',')
    else:
        log_file_path = []

    HEADERS = {
        'content-type': 'application/json',
        'X-Auth-Token': module.params['token'],
        'X-Auth-Type': module.params['auth_type'],
        }

    try:
        f = open(filename, 'r')
        data = f.read()
    except:
        module.fail_json(msg='Unable to read JSON file',
                         meta={'filename': filename})

    # new_plugin contains the plugin configuration passed to Ansible.  The data
    # read from the JSON file contains a 'status' field that is output by the
    # Agent.  This 'status' field is not part of the expected schema for
    # POST'ing to the Controller, and it is ignored by the Controller.
    # Likewise, the 'status' field is not present in the response from the
    # Controller to GET a plugin.
    #
    # Remove the 'status' key from the in-memory representation of the
    # user-specified plugin configuration so that it can be compared the output
    # from the Controller.
    new_plugin = json.loads(data)
    if aggregate_id:
        new_plugin['AggregateId'] = aggregate_id
    if log_file_path:
        for path in log_file_path:
            new_plugin['Config']['CommandLine'] += ' ' + path
    data = json.dumps(new_plugin)
    new_plugin.pop('status', None)
    plugin_id = new_plugin['PluginId']

    # plugin contains the plugin configuration fetched from the Controller
    exists, plugin = is_configured(plugin_url, plugin_id, headers=HEADERS)
    if exists:
        # Check if all fields of `new_plugin' match the existing configuration
        # in `plugin'.  Ignore extra fields that exist only in `plugin'.
        if compare_subset(new_plugin, plugin):
            module.exit_json(changed=False, meta=plugin)
        else:
            # Delete plugin.  It will be re-added below.
            r = requests.delete(url=plugin_url+'/'+plugin_id, headers=HEADERS,
                                verify=CERT_VERIFY_FLAG)
            if r.status_code != 200:
                module.fail_json(
                    msg='Unable to delete plugin',
                    meta={'plugin_id': plugin_id})
            task_id = json.loads(r.text).get('task_id')
            poll_for_task_state(task_url, task_id)

    if new_plugin['PluginName'] == 'contrail.vrouter.flows':
        aggr_id = new_plugin['AggregateId']
        create_aggregate(module=module,
                         plugin_id=plugin_id,
                         aggr_id=aggr_id,
                         aggr_url=aggr_url,
                         headers=HEADERS)

    r = requests.post(url=plugin_url, headers=HEADERS, data=data,
                      verify=CERT_VERIFY_FLAG)
    result={'status': r.status_code, 'response': r.json()}
    if r.status_code != 200:
        module.fail_json(msg='POST failed for plugin', meta=result)
    task_id = json.loads(r.text).get('task_id')
    poll_for_task_state(task_url, task_id)
    module.exit_json(changed=True, meta=result)


if __name__ == '__main__':
    main()
