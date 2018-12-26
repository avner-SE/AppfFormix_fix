from keystoneclient.auth.identity import v3
from keystoneclient import session
from keystoneclient.v3 import client as keystone_client_v3

from common import print_list
from keystone_config import *


# 1. Configure admin Keystone client
auth_plugin = v3.Password(
    auth_url=auth_url_v3,
    username=admin_username,
    password=admin_password,
    project_name=admin_project_name,
    user_domain_name=user_domain_name,
    project_domain_name=project_domain_name)
sess = session.Session(auth=auth_plugin)
ks = keystone_client_v3.Client(session=sess)

# 2. Get token and get token data
token = sess.get_token()
token_data = ks.tokens.get_token_data(token)
print_list('Token', [token, token_data])

# 3. Tenants List
project_list = ks.projects.list()
print_list('Projects', project_list)

# 4. Roles list
roles = ks.roles.list()
print_list('Roles', roles)

# 5. Users List
users = ks.users.list()
print_list('Users', users)

# 6. List roles and projects for a user
user_id = users[0].id
user_roles = ks.role_assignments.list(user=user_id)
print_list('Role assignments for user={0}'.format(user_id), user_roles)

# 7. projects for user
user_projects = ks.projects.list(user=user_id)
print_list('Projects for user={0}'.format(user_id), user_projects)

# 8. domain list
doms = ks.domains.list()
print_list('Domains', doms)
