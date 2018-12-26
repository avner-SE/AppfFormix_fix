#! /usr/bin/env python
import json
import sys
import importlib
from ansible.module_utils.basic import *


def main():
    fields = {
        "config_file_name": {"required": True, "type": "str"},
        "json_file_name": {"required": True, "type": "str"},
        "current_path" :{"required": True, "type": "str"}
    }
    ansible_module = AnsibleModule(argument_spec=fields)
    # get the file_name from the full_path_file_name
    file_name = \
        ansible_module.params['config_file_name'].replace(
            '.py', '').split('/')[-1]
    json_file = ansible_module.params['json_file_name']
    current_path = ansible_module.params['current_path']
    sys.path.append(current_path)
    module = importlib.import_module(file_name)

    aggr_id = module.AGGREGATE_ID
    if not aggr_id:
        aggr_id = 'appformix_network_agents'

    config = {'CommandLine': 'python check_snmp_network_device_template.py',
              'ConfigFile': file_name,
              'EntityType': module.ENTITY_TYPE,
              'PluginPrefix': module.PLUGIN_PREFIX}

    metric_list = [{'Name': entry['Name'], 'Units': entry['Units']}
                   for entry in module.SNMP_MIB_KEYS]

    result = {
        'MetricMap': metric_list,
        'Collection': module.PLUGIN_NAME + '_collection',
        'SnmpOIDList': module.SNMP_OID,
        'AggregateId': aggr_id,
        'status': 'success',
        'PluginType': module.PLUGIN_TYPE,
        'State': 'enabled',
        'PluginName': module.PLUGIN_NAME,
        'PluginId': module.PLUGIN_NAME,
        'Scope': 'snmp_network_device',
        'Config': config
    }

    with open(json_file, 'w') as outfile:
        json.dump(result, outfile)
    ansible_module.exit_json(changed=True, meta=result)


if __name__ == '__main__':
    main()
