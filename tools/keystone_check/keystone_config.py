import os

# Config
auth_url_v2 = os.environ.get('OS_AUTH_URL')
auth_url_v3 = os.environ.get('OS_AUTH_URL')
interface = os.environ.get('OS_ENDPOINT_TYPE', 'publicURL').strip('URL')
endpoint = ''
endpoint_override = ''

user_domain_name = os.environ.get('OS_USER_DOMAIN_NAME', 'Default')
project_domain_name = os.environ.get('OS_PROJECT_DOMAIN_NAME', 'Default')

# Admin Credentials
admin_username = os.environ.get('OS_USERNAME')
admin_password = os.environ.get('OS_PASSWORD')
admin_project_name = os.environ.get('OS_PROJECT_NAME') or os.environ.get('OS_TENANT_NAME')

