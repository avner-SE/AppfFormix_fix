#! /usr/bin/env python2

import collections
import requests
import json
import sys
import traceback

from ansible.module_utils.basic import *

CERT_VERIFY_FLAG = False


def is_config_equal(config, data, exclude=[]):
    ''' Check if key:values in `data' match those in `config', excluding any
        keys in `exclude'.
    '''
    for key,value in data.iteritems():
        if key in exclude:
            continue
        elif isinstance(value, collections.Sequence) \
                and not isinstance(value, basestring):
            if set(value) != set(config[key]):
                return False
        else:
            if str(value) != str(config[key]):
                return False
    return True


class AppFormixScaleIO:
    def __init__(self, module, api_url):
        self.HEADERS = {
            'content-type': 'application/json',
            # Currently, OpenStack Adapter does not use authentication
            #'X-Auth-Token': module.params['token'],
            }
        self.module = module
        self.url = api_url + '/appformix/v1.0/openstack_adapter/scaleio_config'
        self.configured = self._get_configured_clusters()

    def _get_configured_clusters(self):
        r = requests.get(url=self.url, headers=self.HEADERS,
                         verify=CERT_VERIFY_FLAG)
        response = r.json()
        if r.status_code != 200:
            self.module.fail_json(
                msg='GET configuration failed: error={0}'
                    .format(response['message']),
                meta={'url': self.url, 'response': response})
        return {cluster['ScaleIOHost']: cluster
                for cluster in response['ScaleIOConfigs']}

    def post_cluster_config(self, config):
        json_data = json.dumps(config)
        r = requests.post(url=self.url,
                          headers=self.HEADERS,
                          data=json_data, verify=CERT_VERIFY_FLAG)
        if r.status_code != 200:
            config.pop('ScaleIOPass', True)
            self.module.fail_json(
                msg='POST cluster configuration failed',
                meta={'url': self.url, 'config': config, 'response': r.text})
        response = r.json()
        return response

    def delete_cluster_config(self, cluster):
        delete_url = self.url + '/' + cluster['Id']
        r = requests.delete(url=delete_url, headers=self.HEADERS,
                            verify=CERT_VERIFY_FLAG)
        response = r.json()
        if r.status_code != 200:
            self.module.fail_json(
                msg='DELETE cluster configuration failed: error={0}'
                    .format(response['message']),
                meta={'url': delete_url,
                      'name': cluster['ClusterName'],
                      'id': cluster['Id'],
                      'response': response})

    def check_config(self, config):
        changed = False
        existing = self.configured.get(config['ScaleIOHost'])
        if existing is None:
            response = self.post_cluster_config(config)
            changed = True
        elif not is_config_equal(existing, config, exclude=['ScaleIOPass']):
            self.delete_cluster_config(existing)
            response = self.post_cluster_config(config)
            changed = True
        else:
            response = existing
        return changed, response


def generate_cluster_config(module):
    parameter_map = {'name': 'ClusterName',
                     'username': 'ScaleIOUser',
                     'password': 'ScaleIOPass',
                     'host': 'ScaleIOHost',
                     'port': 'ScaleIOPort'}
    config = {parameter_map[k]: module.params[k] for k in parameter_map}
    return config


def main():
    fields = {
        'url': {'required': True, 'type': 'str' },
        'name': {'required': True, 'type': 'str'},
        'host': {'required': True, 'type': 'str'},
        'port': {'default': 80, 'type': 'int'},
        'username': {'required': True, 'type': 'str'},
        'password': {'required': True, 'type': 'str'},
    }
    module = AnsibleModule(argument_spec=fields)

    url = module.params['url']
    cluster_config = generate_cluster_config(module)

    try:
        scaleio = AppFormixScaleIO(module, url)
        changed, response = scaleio.check_config(cluster_config)
        module.exit_json(changed=changed, meta=response)
    except Exception as e:
        module.fail_json(msg=traceback.format_exc(), meta={'url': url, 'cluster': cluster_config})


if __name__ == '__main__':
    main()
