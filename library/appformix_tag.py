#! /usr/bin/env python

import requests
import json
import sys

from ansible.module_utils.basic import *

CERT_VERIFY_FLAG = False


def poll_for_task_state(base_url, task_id):
    header = {'content-type': 'application/json'}
    async_iterations = 20
    async_wait = 1
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
        "token": {"default": "Fake", "type": "str"},
        "auth_type": {"default": "openstack", "type": "str"},
        "hosts": {"required": True, "type": "list"},
        "tag_name": {"required": True, "type": "str"},
        "post_url": {"required": True, "type": "str"},
        "task_url": {"required": True, "type": "str"},
    }
    module = AnsibleModule(argument_spec=fields)

    hosts = module.params['hosts']
    if not hosts:
        module.exit_json(changed=False)
    prefix = 'ansible_bare_host__'
    hosts = [prefix + host.replace('.', '_') for host in hosts]

    HEADERS = {
        'content-type': 'application/json',
        'X-Auth-Token': module.params['token'],
        'X-Auth-Type': module.params['auth_type']
    }

    tag_name = module.params['tag_name']
    post_url = module.params['post_url']
    task_url = module.params['task_url']
    get_url = post_url + '/' + tag_name

    response = requests.get(url=get_url, headers=HEADERS,
                            verify=CERT_VERIFY_FLAG)
    if response.status_code == 404:
        data = {"Name": tag_name,
                "Source": "user",
                "ObjectList": hosts,
                "Type": "host",
                "Id": tag_name,
                "Metadata": "Tag for {0} hosts".format(tag_name)}
        data = json.dumps(data)
        result = requests.post(url=post_url, headers=HEADERS, data=data,
                               verify=CERT_VERIFY_FLAG)
        if result.status_code != 200:
            msg = ('Post failed to url={0} error={1}'.format(post_url,
                                                             result.text))
            module.fail_json(msg=msg)
    elif response.status_code == 200:
        data = {"ObjectList": hosts}
        data = json.dumps(data)
        put_url = post_url + '/' + tag_name
        result = requests.put(url=put_url, headers=HEADERS, data=data,
                              verify=CERT_VERIFY_FLAG)
        if result.status_code != 200:
            msg = ('Put failed to url={0} error={1}'.format(put_url,
                                                            result.text))
            module.fail_json(msg=msg)
        task_id = json.loads(result.text).get('task_id')
        poll_for_task_state(task_url, task_id)
    elif response.status_code != 200:
        data = json.loads(response.text)
        msg = ('Get failed to url={0} error={1}'.format(get_url,
                                                        data['message']))
        module.fail_json(msg=msg)

    module.exit_json(changed=True)


if __name__ == '__main__':
    main()
