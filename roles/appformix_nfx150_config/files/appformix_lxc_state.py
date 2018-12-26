#! /usr/bin/env python

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
import sys

nfx_ip = sys.argv[1]
nfx_user = sys.argv[2]
nfx_pass = sys.argv[3]


def get_appformix_lxc_state(dev):

    vnf_info = dev.rpc.get_virtual_network_functions_information({'format':'json'})
    vnf_list =  vnf_info['vnf-information'][0]['vnf-instance']

    appformix_lxc_state = [vnf['state'][0]['data'] for vnf in vnf_list
                           if vnf['name'][0]['data'] == 'appformix']

    if appformix_lxc_state:
        if appformix_lxc_state == ['Running']:
            print "appformix lxc installed"
        else:
            print "appformix lxc " + appformix_lxc_state[0]
    else:
        print "appformix lxc missing"

def connect():
    # open a connection with the device and start a NETCONF session
    try:
        dev = Device(host=nfx_ip, user=nfx_user, passwd=nfx_pass)
        dev.open()
    except Exception as e:
        print ("Cannot connect to device: {0}".format(e))
        sys.exit(0)
    return dev

def close(dev):
    # End the NETCONF session and close the connection
    dev.close()
    sys.exit(0)

def main():

    dev = connect()
    get_appformix_lxc_state(dev)
    close(dev)


if __name__ == "__main__":
    main()
