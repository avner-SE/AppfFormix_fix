#! /usr/bin/env python
import json
import requests
import sys


auth_token = sys.argv[1]
auth_type = sys.argv[2]
url = sys.argv[3]
process_set_monitors_file = sys.argv[4]
HEADERS = {'content-type': 'application/json'}
HEADERS['X-Auth-Token'] = auth_token
HEADERS['X-Auth-Type'] = auth_type

CERT_VERIFY_FLAG = False


def get_single_process_set_monitor(psm_id):
    try:
        resp = requests.get(url=url + '/' + psm_id,
                            headers=HEADERS, verify=CERT_VERIFY_FLAG)
        if resp.status_code != 200:
            print ('Get fail to process_set_monitor_definition {}: {}'.
                    format(url + '/' + psm_id, resp.text))
            return None
    except Exception as e:
        print 'Exception in get process_set_monitor config {}'.format(e)
        return None
    print 'Successfully got Process Set Monitor'
    return json.loads(resp.text)


def post_single_process_set_monitor(data):
    try:
        resp = requests.post(url=url, data=data,
                             headers=HEADERS, verify=CERT_VERIFY_FLAG)
        if resp.status_code != 200:
            print ('Post fail to process_set_monitor_definition {}: {}'.
                    format(url, resp.text))
            sys.exit(1)
    except Exception as e:
        print 'Exception in post the process_set_monitor config {}'.format(e)
        sys.exit(1)
    print 'Successfully added Process Set Monitor'
    return True


def delete_single_process_set_monitor(psm_id):
    try:
        resp = requests.delete(url=url + "/{0}".format(psm_id),
                               data=None, headers=HEADERS,
                               verify=CERT_VERIFY_FLAG)
        if resp.status_code != 200:
            print ('Delete failed to process_set_monitor_definition {}: {}'.
                   format(url, resp.text))
            return False
    except Exception as e:
        print 'Exception in deleting the process_set_monitor config {}'.\
            format(e)
        return False
    print 'Successfully deleted Process Set Monitor - {}'.format(
        psm_id)
    return True


def process_set_monitors_equal(psm_1, psm_2):
    return psm_1['ProcessList'] == psm_2['ProcessList'] and \
        psm_1['ObjectType'] == psm_2['ObjectType'] and \
        psm_1['ObjectId'] == psm_2['ObjectId'] and \
        psm_1['Status'] == 'enabled'


try:
    with open(process_set_monitors_file) as config_file:
        data = json.loads(config_file.read())
except Exception as e:
    print 'Cannot parse process_set_monitor config file: {0}'.format(e)
    sys.exit(1)

process_set_monitor_list = data['ProcessSetMonitors']

for entry in process_set_monitor_list:
    psm = entry['ProcessSetMonitor']
    psm_id = psm['ProcessSetMonitorId']
    expected_psm = get_single_process_set_monitor(psm_id)
    if (
        expected_psm and
        process_set_monitors_equal(expected_psm['ProcessSetMonitor'], psm)
    ):
        print 'Processed {}: already exists'.format(psm_id)
    else:
        json_data = json.dumps(psm)
        s1 = delete_single_process_set_monitor(psm_id)
        s2 = post_single_process_set_monitor(json_data)
        print 'Processed {}: del status - {}, post status - {}'.format(psm_id,
                                                                       s1, s2)
