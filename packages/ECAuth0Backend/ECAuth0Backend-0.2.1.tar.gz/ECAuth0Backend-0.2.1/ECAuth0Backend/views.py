from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from ECAuth0Backend.settings import AUTH0_CODE_SUCCESS_PATH, AUTH0_CODE_FAILURE_PATH, AUTH0_CODE_LOGOUT_REDIRECT_PATH
from django.contrib.auth import logout


def auth_callback(request):
    """
    View to process the authentication code.
    Redirects to / if already logged in.
    :param request:
    :return:
    """
    if not request.user.is_anonymous:
        return redirect(AUTH0_CODE_SUCCESS_PATH)
    user = authenticate(request=request, **request.GET)
    if user and not user.is_anonymous:
        login(request, user)
        return redirect(request.GET.get('redirect_success', AUTH0_CODE_SUCCESS_PATH))
    else:
        return redirect(request.GET.get('redirect_failed', AUTH0_CODE_FAILURE_PATH))

def auth_login(request):
    return render(request, 'ECAuth0Backend/A0login.html')

def auth_logout(request):
    logout(request)
    return redirect(AUTH0_CODE_LOGOUT_REDIRECT_PATH)

