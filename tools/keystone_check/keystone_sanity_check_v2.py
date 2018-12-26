from keystoneclient.auth.identity import v2
from keystoneclient import session
from keystoneclient.v2_0 import client as keystone_client_v2

from common import print_list
from keystone_config import *


# 1. Configure admin Keystone client
auth_plugin = v2.Password(
    auth_url=auth_url_v2,
    username=admin_username,
    password=admin_password,
    tenant_name=admin_project_name)
sess = session.Session(auth=auth_plugin)
ks = keystone_client_v2.Client(session=sess, interface=interface)

# 2. Get token and get token data
token = sess.get_token()
token_data = ks.tokens.get_token_data(token)
print_list('Token', [token, token_data])

# 3. Tenants List
project_list = ks.tenants.list()
print_list('Projects', project_list)

# 4. Roles list
roles = ks.roles.list()
print_list('Roles', roles)

# 5. Users List
users = ks.users.list()
print_list('Users', users)

# 6. List Users for Tenant
project_id = project_list[0].id
users_for_tenant = ks.tenants.list_users(project_id)
print_list('Users for tenant={0}'.format(project_id), users_for_tenant)

# 7. List Roles for a User for a Tenant
user_id = users[0].id
user_roles = ks.users.list_roles(user=user_id, tenant=project_id)
print_list('Roles for user={0} tenant={0}'.format(user_id, project_id),
           user_roles)
