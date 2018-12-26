#! /usr/bin/env python
import requests
import json
import sys
import importlib

from ansible.module_utils.basic import *


rabbit_config_url = ''
HEADERS = {'content-type': 'application/json'}

CERT_VERIFY_FLAG = False


def cluster_is_equal(cluster, data):
    for key in data:
        if key == 'RabbitPassword':
            continue
        elif key == 'RabbitNodeConfig':
            if data[key] != cluster[key]:
                return False
        else:
            if str(data[key]) != str(cluster[key]):
                return False
    return True


def find_rabbit_config(module, cluster_name):
    response = requests.get(url=rabbit_config_url, headers=HEADERS,
                            verify=CERT_VERIFY_FLAG)
    result = json.loads(response.text)
    if response.status_code != 200:
        module.fail_json(
            msg='GET RabbitMQ config failed: {0}'.format(result['message']),
            url=rabbit_config_url,
            response=result)

    for cluster in result['RabbitMQConfigs']:
        if cluster['ClusterName'] == cluster_name:
            return cluster
    return None


def post_rabbit_config(module, data):
    json_data = json.dumps(data)
    response = requests.post(url=rabbit_config_url,
                             headers=HEADERS, data=json_data,
                             verify=CERT_VERIFY_FLAG)

    if response.status_code != 200:
        result = json.loads(response.text)
        module.fail_json(
            msg='POST RabbitMQ cluster failed: {0}'.format(result['message']),
            url=rabbit_config_url,
            cluster_name=data['ClusterName'],
            response=result)


def update_rabbit_config(module, data, cluster_id):
    json_data = json.dumps(data)
    url = rabbit_config_url + '/' + cluster_id
    response = requests.put(url=url,
                            headers=HEADERS, data=json_data,
                            verify=CERT_VERIFY_FLAG)

    if response.status_code != 200:
        result = json.loads(response.text)
        module.fail_json(
            msg='PUT RabbitMQ cluster failed: {0}'.format(result['message']),
            url=rabbit_config_url,
            cluster_name=data['ClusterName'],
            response=result)


def main():
    fields = {
        "base_url": {"required": True, "type": "str"},
        "nodes": {"required": True, "type": "list"},
        "username": {"required": True, "type": "str"},
        "password": {"required": True, "type": "str", "no_log": True},
        "cluster_name": {"default": "default_mysql_cluster", "type": "str"},
    }
    module = AnsibleModule(argument_spec=fields)

    nodes = module.params['nodes']
    if not nodes:
        module.exit_json(changed=False)
    for node in nodes:
        if (
            'RabbitUrl' not in node
            or 'RabbitNode' not in node
            or 'AgentUrl' not in node
        ):
            msg = 'Invalid RabbitNodeConfig: {0}'.format(node)
            module.fail_json(msg=msg)

    data = {
        "ClusterName": module.params['cluster_name'],
        "RabbitNodeConfig": nodes,
        "RabbitPassword": module.params['password'],
        "RabbitUser": module.params['username'],
    }

    global rabbit_config_url
    rabbit_config_url = module.params['base_url'] + '/rabbit_config'

    cluster_config = find_rabbit_config(module, data['ClusterName'])
    if cluster_config is None:
        post_rabbit_config(module, data)
        module.exit_json(changed=True)
    elif not cluster_is_equal(cluster_config, data):
        update_rabbit_config(module, data, cluster_config['ClusterId'])
        module.exit_json(changed=True)

    module.exit_json(changed=False)


if __name__ == "__main__":
    main()
