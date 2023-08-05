from django.conf import settings

AUTH0_DOMAIN = getattr(settings, 'AUTH0_DOMAIN', None)

AUTH0_CODE_CLIENT_ID = getattr(settings, 'AUTH0_CODE_CLIENT_ID', None)
AUTH0_CODE_CLIENT_SECRET = getattr(settings, 'AUTH0_CODE_CLIENT_SECRET', None)
AUTH0_CODE_CALLBACK_PATH = getattr(settings, 'AUTH0_CODE_CALLBACK_PATH', '/auth_callback/')
AUTH0_CODE_LOGIN_PATH = getattr(settings, 'AUTH0_CODE_LOGIN_PATH', '/login/')
AUTH0_CODE_SUCCESS_PATH = getattr(settings, 'AUTH0_CODE_SUCCESS_PATH', '/success/')
AUTH0_CODE_FAILURE_PATH = getattr(settings, 'AUTH0_CODE_FAILURE_PATH', '/failed/')
AUTH0_CODE_LOGOUT_PATH = getattr(settings, 'AUTH0_CODE_LOGOUT_PATH', '/logout/')
AUTH0_CODE_LOGOUT_REDIRECT_PATH = getattr(settings, 'AUTH0_CODE_LOGOUT_REDIRECT_PATH', '/')

AUTH0_CODE_CALLBACK_PATTERN = getattr(settings, 'AUTH0_CODE_CALLBACK_PATTERN', r'^{path}$'.format(
    path=AUTH0_CODE_CALLBACK_PATH[1:]
))
AUTH0_CODE_LOGIN_PATTERN = getattr(settings, 'AUTH0_CODE_LOGIN_PATTERN', r'^{path}$'.format(
    path=AUTH0_CODE_LOGIN_PATH[1:]
))
AUTH0_CODE_LOGOUT_PATTERN = getattr(settings, 'AUTH0_CODE_LOGOUT_PATTERN', r'^{path}$'.format(
    path=AUTH0_CODE_LOGOUT_PATH[1:]
))

AUTH0_JWT_SECRET = getattr(settings, 'AUTH0_JWT_SECRET', None)
AUTH0_JWT_CLIENT_ID = getattr(settings, 'AUTH0_JWT_CLIENT_ID', None)
AUTH0_JWT_HEADER_SEPARATOR = getattr(settings, 'AUTH0_JWT_HEADER_SEPARATOR', 'JWT')
