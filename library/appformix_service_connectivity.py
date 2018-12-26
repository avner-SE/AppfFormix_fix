#! /usr/bin/env python2

import requests
import json
import sys
import ast
from ansible.module_utils.basic import *

CERT_VERIFY_FLAG = False


def post_service_group(service_group, profile_url,
                       headers, module):
    data = json.dumps(service_group)
    resp = requests.post(url=profile_url, data=data,
                         headers=headers, verify=CERT_VERIFY_FLAG)
    if resp.status_code != 200:
        print ("Post fail to profile_url {}: {}".
               format(profile_url, resp.text))
        module.fail_json(msg='POST failed for profile', meta=resp.text)
        sys.exit(1)


# Check if profile is already configured, and return its configuration.
def is_configured(url, profile_id, headers={}):
    r = requests.get(url=url+'/'+profile_id, headers=headers,
                     verify=CERT_VERIFY_FLAG)
    if r.status_code == 200:
        p = r.json()['Profile']
        return True, p
    return False, None


def main():

    fields = {
        "json_file": {"required": True, "type": "str"},
        "profile_url": {"required": True, "type": "str" },
        "token": {"default": "Fake", "type": "str"},
        "auth_type": {"default": "openstack", "type": "str"}
    }
    module = AnsibleModule(argument_spec=fields)

    profile_url = str(module.params['profile_url']).strip()
    filename = module.params['json_file']
    service_group_config = json.loads(filename)
    #new_profile = data

    HEADERS = {
        'content-type': 'application/json',
        'X-Auth-Token': str(module.params['token']).strip(),
        'X-Auth-Type': str(module.params['auth_type']).strip(),
        }

    if not service_group_config:
        raise Exception("Service Group Config not valid")
    post_service_group(service_group_config, profile_url, HEADERS, module)

    module.exit_json(changed=True)


if __name__ == '__main__':
    main()
