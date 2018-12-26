#! /usr/bin/env python
import requests
import json
import sys


base_url = sys.argv[1]
cassandra_host = sys.argv[2]
cassandra_cluster_name = sys.argv[3]
if len(sys.argv) > 4:
    cassandra_username = sys.argv[4]
    cassandra_password = sys.argv[5]
else:
    cassandra_username = ""
    cassandra_password = ""

data = {
    "ClusterName": cassandra_cluster_name,
    "CassHost": cassandra_host,
    "CassPass": cassandra_password,
    "CassUser": cassandra_username
}

cassandra_config_url = base_url + '/cass_config'
HEADERS = {'content-type': 'application/json'}
delete_url = ''

CERT_VERIFY_FLAG = False


def cluster_is_equal(cluster, data):
    for key in data:
        if key == 'ContrailPass':
            continue
        else:
            if str(data[key]) != str(cluster[key]):
                return False
    return True


def delete_cassandra_config_entry():
    global delete_url
    if delete_url == '':
        return
    response = requests.delete(url=delete_url, headers=HEADERS,
                               verify=CERT_VERIFY_FLAG)
    if response.status_code != 200:
        result = json.loads(response.text)
        raise Exception('Delete Cassandra cluster failed url={0} name={1} error={2}'.
                        format(delete_url,
                               cassandra_cluster_name,
                               result['message']))


def check_cassandra_config():
    response = requests.get(url=cassandra_config_url,
                            headers=HEADERS, verify=CERT_VERIFY_FLAG)
    result = json.loads(response.text)
    if response.status_code != 200:
        raise Exception('Get Cassandra configs list failed url={0} error={1}'.
                        format(cassandra_config_url,
                               result['message']))

    for cluster in result['CassConfigs']:
        if cluster['ClusterName'] == cassandra_cluster_name:
            if cluster_is_equal(cluster, data):
                return True
            else:
                global delete_url
                delete_url = cassandra_config_url + '/' + cluster['Id']
                return False
    return False


def post_cassandra_config():
    json_data = json.dumps(data)
    response = requests.post(url=cassandra_config_url,
                             headers=HEADERS, data=json_data,
                             verify=CERT_VERIFY_FLAG)
    if response.status_code != 200:
        result = json.loads(response.text)
        raise Exception('Post Cassandra cluster failed url={0} name={1} error={2}'.
                        format(cassandra_config_url,
                               cassandra_cluster_name,
                               result['message']))


if __name__ == "__main__":
    if not check_cassandra_config():
        delete_cassandra_config_entry()
        post_cassandra_config()
