from django import template
from ECAuth0Backend import settings
from ECAuth0Backend.backend import get_redirect_uri

register = template.Library()

@register.simple_tag
def auth0_domain():
    return settings.AUTH0_DOMAIN

@register.simple_tag
def auth0_jwt_client_id():
    return settings.AUTH0_JWT_CLIENT_ID

@register.simple_tag
def auth0_jwt_header_separator():
    return settings.AUTH0_JWT_HEADER_SEPARATOR

@register.simple_tag
def auth0_code_client_id():
    return settings.AUTH0_CODE_CLIENT_ID

@register.simple_tag
def auth0_code_callback_path():
    return settings.AUTH0_CODE_CALLBACK_PATH

@register.simple_tag(takes_context=True)
def auth0_code_callback_url(context):
    request = context['request']
    return get_redirect_uri(request)

