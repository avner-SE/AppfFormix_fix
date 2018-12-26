#! /usr/bin/env python
import argparse
import requests
import json
import time

parser = argparse.ArgumentParser()
parser.add_argument(
    '-token', '--token', type=unicode, required=True,
    help='No token provided')
parser.add_argument(
    '-auth_type', '--auth_type', type=unicode, required=True,
    help='No auth type provided')
parser.add_argument(
    '-host', '--host', type=unicode, required=True,
    help='No host provided')
parser.add_argument(
    '-url', '--url', type=unicode, required=True,
    help='No url provided')
parser.add_argument(
    '-task_url', '--task_url', type=unicode, required=True,
    help='No task_url provided')
parser.add_argument(
    '-source', '--source', type=unicode, required=True,
    help='No source provided')
parser.add_argument(
    '-snmp_ip', '--snmp_ip', type=unicode, required=True,
    help='No snmp_ip provided')
parser.add_argument(
    '-snmp_user', '--snmp_user', type=unicode, required=True,
    help='No snmp_user provided')
parser.add_argument(
    '-snmp_pwd', '--snmp_pwd', type=unicode, required=True,
    help='No snmp_pwd provided')
parser.add_argument(
    '-snmp_community', '--snmp_community', type=unicode, required=True,
    help='No snmp_community provided')
parser.add_argument(
    '-snmp_level', '--snmp_level', type=unicode, required=True,
    help='No snmp_level provided')
parser.add_argument(
    '-snmp_protocol', '--snmp_protocol', type=unicode, required=True,
    help='No snmp_protocol provided')
parser.add_argument(
    '-snmp_version', '--snmp_version', type=unicode, required=True,
    help='No snmp_version provided')
parser.add_argument(
    '-snmp_priv', '--snmp_priv', type=unicode, required=True,
    help='No snmp_version provided')
parser.add_argument(
    '-snmp_priv_protocol', '--snmp_priv_protocol', type=unicode, required=True,
    help='No snmp_version provided')
parser.add_argument(
    '-ipmi_ip', '--ipmi_ip', type=unicode, required=True,
    help='No ipmi_ip provided')
parser.add_argument(
    '-ipmi_user', '--ipmi_user', type=unicode, required=True,
    help='No ipmi_user provided')
parser.add_argument(
    '-ipmi_pwd', '--ipmi_pwd', type=unicode, required=True,
    help='No ipmi_pwd provided')
args = parser.parse_args()

if args.snmp_ip != "not_configured":
    if args.snmp_version == '3':
        snmp_obj = {'Version': args.snmp_version,
                    'Username': args.snmp_user,
                    'Password': args.snmp_pwd,
                    'Protocol': args.snmp_protocol,
                    'Level': args.snmp_level,
                    'Ip': args.snmp_ip}
        if args.snmp_priv != "not_configured":
            snmp_obj['PrivKey'] = args.snmp_priv
            snmp_obj['PrivProtocol'] = args.snmp_priv_protocol
    else:
        snmp_obj = {'Version': args.snmp_version,
                    'Community': args.snmp_community,
                    'Ip': args.snmp_ip}
else:
    snmp_obj = None

if args.ipmi_ip != "not_configured":
    ipmi_obj = {'Username': args.ipmi_user,
                'Password': args.ipmi_pwd,
                'Ip': args.ipmi_ip}
else:
    ipmi_obj = None

async_iterations = 20
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


# Use a unique ID namespace for bare hosts configured by Ansible role
server_id = 'ansible_remote_host__' + args.host.replace('.', '_')

get_url = args.url + '/' + server_id
HEADERS = {'content-type': 'application/json'}
link_capacity = '10G'
HEADERS['X-Auth-Token'] = args.token
HEADERS['X-Auth-Type'] = args.auth_type

response = requests.get(url=get_url, headers=HEADERS, verify=CERT_VERIFY_FLAG)
if response.status_code == 404:
    base_url = 'http://' + args.host + ':42595'
    data = {"Name": args.host, "HostName": args.host,
            "LinkCapacity": link_capacity,
            "ServerId": server_id, "Source": args.source,
            "AgentBaseUrl": 'fake_url',
            "MetaData": {'IpmiConfig': ipmi_obj, 'SnmpConfig': snmp_obj}}
    data = json.dumps(data)
    result = requests.post(url=args.url, headers=HEADERS, data=data,
                           verify=CERT_VERIFY_FLAG)
    if result.status_code != 200:
        raise Exception('Post failed to url={0}, data={1}, error={2}'.
                        format(args.url, data, result.text))
    task_id = json.loads(result.text).get('task_id')
    poll_for_task_state(args.task_url, task_id)
elif response.status_code != 200:
    data = json.loads(response.text)
    raise Exception('Get failed to url={0}, error={1}'.
                    format(get_url, data['message']))
