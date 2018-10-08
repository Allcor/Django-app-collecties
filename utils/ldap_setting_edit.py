from django_python3_ldap.utils import format_username_active_directory, format_search_filters
from django_python3_ldap.conf import settings

def format_username_or_email(model_fields):
    username = model_fields['username']
    if '@' in username:
        return username
    else:
        return format_username_active_directory(model_fields)

def format_search_user_or_email(ldap_fields):
    user_field = settings.LDAP_AUTH_USER_FIELDS['username']
    email_user_field = 'userPrincipalName'
    username = ldap_fields[user_field]
    if '@' in username:
        ldap_fields[email_user_field] = ldap_fields.pop(user_field)
    return format_search_filters(ldap_fields)