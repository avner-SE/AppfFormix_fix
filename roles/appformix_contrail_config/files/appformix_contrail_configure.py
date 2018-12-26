#! /usr/bin/env python
import requests
import json
import sys


base_url = sys.argv[1]
contrail_cluster_name = sys.argv[2]
contrail_analytics_url = sys.argv[3]
contrail_config_url = sys.argv[4]
contrail_token = sys.argv[5]


data = {
    "ClusterName": contrail_cluster_name,
    "ContrailAnalyticsURL": contrail_analytics_url,
    "ContrailConfigURL": contrail_config_url,
    "ContrailToken": contrail_token
}

openstack_adapter_contrail_config_url = base_url + '/contrail_config'
HEADERS = {'content-type': 'application/json'}
put_url = ''

CERT_VERIFY_FLAG = False


def cluster_is_equal(cluster, data):
    for key in data:
        if key == 'ContrailToken':
            continue
        else:
            if str(data[key]) != str(cluster[key]):
                return False
    return True


def check_contrail_config_exists():
    response = requests.get(url=openstack_adapter_contrail_config_url,
                            headers=HEADERS, verify=CERT_VERIFY_FLAG)
    result = json.loads(response.text)
    if response.status_code != 200:
        raise Exception('Get Contrail configs list failed url={0} error={1}'.
                        format(openstack_adapter_contrail_config_url,
                               result['message']))

    return result['ContrailConfigs']


def check_contrail_config(contrail_config):
    # We only allow one contrail cluster in AppFormix
    cluster = contrail_config[0]
    if cluster_is_equal(cluster, data):
        return True
    else:
        global put_url
        put_url = openstack_adapter_contrail_config_url + '/' + cluster['Id']
        return False


def post_contrail_config():
    json_data = json.dumps(data)
    response = requests.post(url=openstack_adapter_contrail_config_url,
                             data=json_data, headers=HEADERS,
                             verify=CERT_VERIFY_FLAG)
    result = json.loads(response.text)
    if response.status_code != 200:
        raise Exception('Post Contrail configs failed data={0} error={1}'.
                        format(data,
                               result['message']))


def update_contrail_config():
    json_data = json.dumps(data)
    response = requests.put(url=put_url,
                            headers=HEADERS, data=json_data,
                            verify=CERT_VERIFY_FLAG)
    if response.status_code != 200:
        result = json.loads(response.text)
        raise Exception('Post Contrail cluster failed url={0} name={1} error={2}'.
                        format(openstack_adapter_contrail_config_url,
                               contrail_cluster_name,
                               result['message']))


if __name__ == "__main__":
    contrail_config = check_contrail_config_exists()
    if not contrail_config:
        post_contrail_config()
    elif not check_contrail_config(contrail_config):
        update_contrail_config()
