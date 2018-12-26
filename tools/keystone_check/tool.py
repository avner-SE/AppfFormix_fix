import os

if __name__ == '__main__':
    keystone_api_version = int(os.environ.get('OS_IDENTITY_API_VERSION', 2))
    if keystone_api_version == 2:
        print "Checking Keystone using API v2"
        import keystone_sanity_check_v2
    elif keystone_api_version == 3:
        print "Checking Keystone using API v3"
        import keystone_sanity_check_v3
    else:
        print "Unsupported OS_IDENTITY_API_VERSION='{0}'".format(keystone_api_version)
