from django.conf.urls import url
from ECAuth0Backend import views
from ECAuth0Backend import settings

urlpatterns = [
    url(settings.AUTH0_CODE_CALLBACK_PATTERN, views.auth_callback, name='a0_auth_callback'),
    url(settings.AUTH0_CODE_LOGIN_PATTERN, views.auth_login, name='a0_login'),
    url(settings.AUTH0_CODE_LOGOUT_PATTERN, views.auth_logout, name='a0_logout'),
]
