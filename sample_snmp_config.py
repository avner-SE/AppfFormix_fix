# a list of oids which you want to run
SNMP_OID = []
# a list of metrics you want to collect from above oids, we also need to
# specify the unit of this metric and the CalculationMethod of this metric, if you
# want AppFormix to calculate the rate of this metric, you should put 'rate'
# here, otherwise, put value(and we will not do any calculation)
SNMP_MIB_KEYS = [
    {'Name': 'jnxOperatingTemp', 'Units': 'C',
     'CalculationMethod': 'value'}
    {'Name': 'jnxOperatingCPU', 'Units': '%',
     'CalculationMethod': 'value'}
]
# there are four types of snmp plugins: snmp_network_device, snmp_device_info,
# snmp_device_attribute and snmp_custom.
# snmp_network_device refer to tabular mibs which define multiple
# related object instances grouped in MIB tables e.g. ifTable defined the
# metrics for a list of interfaces in this device.
# snmp_device_info refer to singular mibs which define a single object
# instance, e.g. 1.3.6.1.2.1.1.7(oid for sysServices). you can specify by OID
# and name it.
# snmp_device_attribute refer to the case which we don't have a field to
# determine the tag for each entry in tabular mibs. Instead, the sample snmp
# output of these mibs are metric_name.x.x.x.x = value which x.x.x.x is the tag
# name. e.g. oid 1.3.6.1.4.1.9.9.42.1.1.8.1(oid for CISCO-RTTMON-MIB)
PLUGIN_TYPE = 'snmp_network_device'
# plugin name of your plugin, can be anything you like, but cannot be reused by
# other plugins
PLUGIN_NAME = 'snmp_network_device_usage'
# this field is required for tabular(plugin_type=snmp_network_device) mibs to
# determine the tag for each entry of the snmp output. This field is not needed
# for singular mibs(plugin_type=device_info)
SNMP_TAG_KEY = 'jnxOperatingDescr'
# you can leave it empty string, default aggregate_id is appformix_platform
AGGREGATE_ID = ''
# plugin prefix, optional. This will be the prefix of the metrics shown in
# AppFormix Dashboard. For example, for oid IF-MIB::ifTable, the prefix could
# be "interface"
PLUGIN_PREFIX = ''
# Entity Type is a list of strings. It indicates what is this mib's data
# for. If it reports interface data, ENTITY_TYPE=['interface'], if it reports
# both FAN and FPC data, ENTITY_TYPE=['FAN', 'FPC'], if it reports the device
# data, ENTITY_TYPE=['network_device']
ENTITY_TYPE = []
