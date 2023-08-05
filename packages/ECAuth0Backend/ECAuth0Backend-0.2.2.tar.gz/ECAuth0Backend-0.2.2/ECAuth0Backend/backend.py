import json
import logging

import requests
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest

from ECAuth0Backend.models import A0User
from ECAuth0Backend.settings import AUTH0_DOMAIN, AUTH0_CODE_CLIENT_ID, AUTH0_CODE_CLIENT_SECRET, \
    AUTH0_CODE_CALLBACK_PATH


def get_or_create_user(user_id, email, email_verified, name, profile=None):
    """
    Get or create a user.
    :user_id: the Auth0 user_id
    :email: the user's email
    :email_verified: whether or not the user's email is verified
    :name: the user's name
    :return:
    """
    logging.warning(profile)
    try:
        user = A0User.objects.get(uid=user_id)
        user.email = email
        user.email_verified = email_verified
        user.name = name
        if profile and not user.profile:
            user.profile = profile
        elif profile and user.profile:
            user.profile.update(profile)
        user.save()
    except A0User.DoesNotExist:
        user_data = {
            "uid": A0User.normalize_username(user_id),
            "email": email,
            "email_verified": email_verified,
            "name": name
        }
        if profile:
            user_data['profile'] = profile
        user = A0User.objects.create(**user_data)
    return user


def _get_protocol(request):
    return "https" if (request.is_secure() or request.META.get('HTTP_X_FORWARDED_PROTO', "") == "https") else "http"


def get_redirect_uri(request):
    return "{protocol}://{host}{path}".format(
        protocol=_get_protocol(request),
        host=request.get_host(),
        path=AUTH0_CODE_CALLBACK_PATH
    )


class Auth0Backend(object):
    def get_user(self, user_id):
        user = None
        if type(user_id) is int:
            try:
                user = A0User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass
        else:
            try:
                user = A0User.objects.get(uid=user_id)
            except User.DoesNotExist:
                pass
        return user

    def authenticate(self, **credentials):
        if credentials.get('username') and credentials.get('password'):
            user = A0User.objects.get_by_natural_key(credentials.get('username'))
            logging.warning(user)
            if user.check_password(credentials.get('password')):
                return user

        request = credentials.get('request')
        authorization_code = credentials.get('code')
        if not authorization_code or not request:
            return None
        else:
            authorization_code = authorization_code[0]
        json_header = {'content-type': 'application/json'}
        token_url = "https://{domain}/oauth/token".format(
            domain=AUTH0_DOMAIN
        )
        token_payload = {
            'client_id': AUTH0_CODE_CLIENT_ID,
            'client_secret': AUTH0_CODE_CLIENT_SECRET,
            'redirect_uri': get_redirect_uri(request),
            'code': authorization_code,
            'grant_type': 'authorization_code'
        }
        token_info = requests.post(token_url, data=json.dumps(token_payload), headers=json_header).json()
        try:
            user_url = "https://{domain}/userinfo?access_token={access_token}".format(
                domain=AUTH0_DOMAIN,
                access_token=token_info['access_token']
            )
        except KeyError:
            raise HttpResponseBadRequest

        user_info = requests.get(user_url).json()

        return get_or_create_user(
            user_id=user_info.get('sub'),
            email=user_info.get('email'),
            email_verified=user_info.get('email_verified', False),
            name=user_info.get('name'),
            profile=user_info,
        )
