#! /usr/bin/env python
import requests
import json
import sys

from ansible.module_utils.basic import *


put_url = ''
mysql_config_url = ''
mysql_cluster_name = ''
HEADERS = {'content-type': 'application/json'}

CERT_VERIFY_FLAG = False


def cluster_is_equal(cluster, data):
    global put_url
    put_url = mysql_config_url + '/' + cluster['Id']
    for key in data:
        if key == 'MySQLHostConfig':
            if data[key] != cluster[key]:
                return False
        elif key == 'MySQLPass':
            continue
        else:
            if str(data[key]) != str(cluster[key]):
                return False
    return True


def update_mysql_config(module, data):
    if put_url == '':
        return
    json_data = json.dumps(data)
    response = requests.put(url=put_url,
                            headers=HEADERS, data=json_data,
                            verify=CERT_VERIFY_FLAG)
    if response.status_code != 200:
        result = json.loads(response.text)
        module.fail_json(
            msg='PUT MySQL cluster failed: {0}'.format(result['message']),
            url=put_url,
            cluster_name=mysql_cluster_name,
            response=result)


def get_mysql_config(module, data):
    response = requests.get(url=mysql_config_url, headers=HEADERS,
                            verify=CERT_VERIFY_FLAG)
    result = json.loads(response.text)
    if response.status_code != 200:
        module.fail_json(
            msg='GET MySQL config failed: {0}'.format(result['message']),
            url=mysql_config_url,
            response=result)
    for cluster in result['MySQLConfigs']:
        if cluster['ClusterName'] == mysql_cluster_name:
            return cluster
    return None


def post_mysql_config(module, data):
    json_data = json.dumps(data)
    response = requests.post(url=mysql_config_url,
                             headers=HEADERS, data=json_data,
                             verify=CERT_VERIFY_FLAG)
    if response.status_code != 200:
        result = json.loads(response.text)
        module.fail_json(
            msg='POST MySQL cluster failed: {0}'.format(result['message']),
            url=mysql_config_url,
            cluster_name=mysql_cluster_name,
            response=result)

def main():
    fields = {
        "base_url": {"required": True, "type": "str"},
        "hosts": {"required": True, "type": "list"},
        "username": {"required": True, "type": "str"},
        "password": {"required": True, "type": "str", "no_log": True},
        "cluster_name": {"default": "default_mysql_cluster", "type": "str"},
        "port": {"default": "3306", "type": "int"},
    }
    module = AnsibleModule(argument_spec=fields)

    hosts = module.params['hosts']
    if not hosts:
        module.exit_json(changed=False)
    for host in hosts:
        if 'MySQLHost' not in host or 'AgentUrl' not in host:
            msg = 'Invalid MySQLHostConfig: {0}'.format(host)
            module.fail_json(msg=msg)

    data = {
        "ClusterName": module.params['cluster_name'],
        "MySQLHostConfig": hosts,
        "MySQLPass": module.params['password'],
        "MySQLPort": module.params['port'],
        "MySQLUser": module.params['username'],
    }

    global mysql_config_url
    mysql_config_url = module.params['base_url'] + '/mysql_config'
    global mysql_cluster_name
    mysql_cluster_name = module.params['cluster_name']

    mysql_config = get_mysql_config(module, data)
    if not mysql_config:
        post_mysql_config(module, data)
    elif not cluster_is_equal(mysql_config, data):
        update_mysql_config(module, data)
        module.exit_json(changed=True)

    module.exit_json(changed=False)


if __name__ == "__main__":
    main()
