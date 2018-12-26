#! /usr/bin/env python2

import requests
import json
import sys
from ansible.module_utils.basic import *


def post_cluster(module, cluster_url, data, headers):
    r = requests.post(url=cluster_url, data=data, headers=headers)
    output = r.json()
    if r.status_code != 200:
        module.fail_json(msg='Could not add cluster {0}: {1}'.
                         format(cluster_name, output))
    return output['Cluster']['ClusterId']


def create_cluster_json(args):
    data = {'Name': args['cluster_name'],
            'ControllerConfig': {
                'Host': args['cluster_controller_host'],
                'Port': args['cluster_controller_port']
                },
            'Credentials': {
                'AuthType': args['cluster_auth_type']
                }
            }
    if args['cluster_username'] and args['cluster_password']:
        data['Credentials']['UserName'] = args['cluster_username']
        data['Credentials']['Password'] = args['cluster_password']
    elif args['cluster_token']:
        data['Credentials']['Token'] = args['cluster_token']

    return json.dumps(data)


def cluster_matches(cluster, args):
    cluster = cluster['Cluster']
    if (cluster['Name'] == args['cluster_name'] and
            cluster['ControllerConfig']['Host'] == args['cluster_controller_host'] and
            cluster['ControllerConfig']['Port'] == str(args['cluster_controller_port']) and
            cluster['Credentials']['AuthType'] == args['cluster_auth_type']):
        return True
    return False


def get_cluster_id(module, cluster_url, headers, args):
    r = requests.get(url=cluster_url, data=None, headers=headers)
    output = r.json()
    if r.status_code != 200:
        module.fail_json(msg="Could not get cluster list with URL {0}: {1}".
                         format(cluster_url, output))
    clusters = output['ClusterProfile']
    for cluster in clusters:
        if cluster_matches(cluster, args):
            return cluster['Cluster']['ClusterId']
    return None


def delete_cluster(module, cluster_url, headers, cluster_id):
    r = requests.delete(cluster_url + '/' + cluster_id, data=None,
                        headers=headers)
    output = r.json()
    if r.status_code != 200:
        module.fail_json(msg='Could not delete cluster {0}: {1}'.
                         format(cluster_id, output))


def main():
    fields = {
        "cluster_config_url": {"required": True, "type": "str"},
        "token": {"required": True, "type": "str"},
        "auth_type": {"required": True, "type": "str"},
        "cluster_name": {"required": True, "type": "str" },
        "cluster_controller_host": {"required": True, "type": "str" },
        "cluster_controller_port": {"required": True, "type": "int" },
        "cluster_auth_type": {"required": True, "type": "str" },
        "cluster_username": {"required": True, "type": "str" },
        "cluster_password": {"required": True, "type": "str" },
        "cluster_token": {"required": True, "type": "str" },
        "action": {"required": True, "type": "str"}
    }
    module = AnsibleModule(argument_spec=fields)

    cluster_config_url = module.params['cluster_config_url']
    action = module.params['action']

    HEADERS = {
        'content-type': 'application/json',
        'X-Auth-Token': module.params['token'],
        'X-Auth-Type': module.params['auth_type'],
        }

    if action == 'add':
        cluster_id = get_cluster_id(module=module,
                                    cluster_url=cluster_config_url,
                                    headers=HEADERS,
                                    args=module.params)
        if cluster_id:
            module.exit_json(changed=False, meta=cluster_id)
        data = create_cluster_json(args=module.params)
        cluster_id = post_cluster(module=module,
                                  cluster_url=cluster_config_url,
                                  data=data,
                                  headers=HEADERS)
    elif action == 'delete':
        cluster_id = get_cluster_id(module=module,
                                    cluster_url=cluster_config_url,
                                    headers=HEADERS,
                                    args=module.params)
        if not cluster_id:
            module.fail_json(msg='Could not find cluster with parameters {0}'.
                format(module.params))
        delete_cluster(module=module,
                       cluster_url=cluster_config_url,
                       headers=HEADERS,
                       cluster_id=cluster_id)
    else:
        module.fail_json(msg='Invalid action {0} in script '
                         'appformix_cluster_config'.format(action))

    module.exit_json(changed=True, meta=cluster_id)


if __name__ == '__main__':
    main()
