#! /usr/bin/env python

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
import sys

conf = sys.argv[1]

nfx_ip = sys.argv[2]
nfx_user = sys.argv[3]
nfx_pass = sys.argv[4]

def delete_appformix_lxc(dev):
    dev.cu.load('delete virtual-network-functions appformix')

def set_appformix_lxc(dev):
    dev.cu.load(path=conf, merge=True)

def connect():
    # Open a connection with the device and start a NETCONF session
    try:
        dev = Device(host=nfx_ip, user=nfx_user, passwd=nfx_pass)
        dev.open()
    except Exception as e:
        print ("Cannot connect to device: {0}".format(e))
        sys.exit(0)
    return dev

def bind_config(dev):
    # Bind the Config instance to the Device instance.
    dev.bind(cu=Config)

def lock_config(dev):
    print ("Locking the configuration")
    try:
        dev.cu.lock()
    except Exception as e:
        print ("Unable to lock configuration: {0}".format(e))
        close(dev)

def load_config(dev):
    print ("Loading configuration changes")
    try:
        if conf != "clean":
            set_appformix_lxc(dev)
        else:
            delete_appformix_lxc(dev)
    except Exception as e:
        print ("Unable to load configuration changes: {0}".format(e))
        unlock_config(dev)
        close(dev)

def commit_config(dev):
    print ("Committing the configuration")
    try:
        dev.cu.commit(comment='Loaded')
    except Exception as e:
        print ("Unable to commit configuration: {0}".format(e))
        unlock_config(dev)
        close(dev)

def unlock_config(dev):
    print ("Unlocking the configuration")
    try:
        dev.cu.unlock()
    except Exception as e:
        print ("Unable to unlock configuration: {0}".format(e))

def close(dev):
    # End the NETCONF session and close the connection
    dev.close()
    sys.exit(0)

def main():
    dev = connect()
    bind_config(dev)
    # Lock the configuration, load configuration changes, and commit
    lock_config(dev)
    load_config(dev)
    commit_config(dev)
    unlock_config(dev)
    close(dev)


if __name__ == "__main__":
    main()
