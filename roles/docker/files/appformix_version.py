#! /usr/bin/env python2

from docker import Client
import re
import sys


def main():
    install_appformix_version = sys.argv[1]
    # Check match for installation of appformix customer version.
    match = re.search(r'(\d+\.\d+\.\d+)$', install_appformix_version)
    if not match:
        return
    install_appformix_version = match.groups()[0].split('.')
    containers = Client().containers()
    for container in containers:
        image = str(container['Image'])
        # Check match for running appformix version
        match = re.search(r'.*appformix.*:(\d+\.\d+\.\d+)$', image)
        if match:
            running_appformix_version = match.groups()[0].split('.')
            # Compare versions to check if its same or later version
            for i in range(3):
                if int(install_appformix_version[i]) > \
                        int(running_appformix_version[i]):
                    return
                elif int(install_appformix_version[i]) == \
                        int(running_appformix_version[i]):
                    continue
                else:
                    sys.exit('Abort: Installing an older version')


if __name__ == "__main__":
    main()
