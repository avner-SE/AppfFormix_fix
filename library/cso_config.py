#! /usr/bin/env python

import requests
import json
import sys

from ansible.module_utils.basic import *

CERT_VERIFY_FLAG = False

def main():
    fields = {
        "data_view_central_url": {"required": True, "type": "str"},
        "regional_controller_urls": {"required": True, "type": "list"},
        "cso_config_post_url": {"required": True, "type": "str"},
    }
    module = AnsibleModule(argument_spec=fields)

    data_view_central_url = module.params['data_view_central_url']
    regional_controller_urls = module.params['regional_controller_urls']
    url = module.params['cso_config_post_url']

    HEADERS = {
        'content-type': 'application/json',
    }

    regional_information = [{'ControllerBaseUrl': item} for item in regional_controller_urls]
    data = {
        'Controllers': regional_information,
        'DataViewCentralUrl': data_view_central_url
    }
    json_data = json.dumps(data)
    response = requests.post(url=url, data=json_data, headers=HEADERS,
                             verify=CERT_VERIFY_FLAG)

    if response.status_code != 200:
        data = json.loads(response.text)
        msg = ('POST failed to url={0} error={1}'.format(url,
                                                         data['message']))
        module.fail_json(msg=msg)

    module.exit_json(changed=True)

if __name__ == '__main__':
    main()

