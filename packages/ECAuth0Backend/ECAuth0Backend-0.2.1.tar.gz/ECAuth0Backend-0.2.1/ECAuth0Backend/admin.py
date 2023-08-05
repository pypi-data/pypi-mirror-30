from django.contrib import admin
from django.contrib.admin.decorators import register

from ECAuth0Backend.models import A0User


@register(A0User)
class NeedAdmin(admin.ModelAdmin):
    list_display = ('uid', 'name', 'email', 'is_staff', 'is_superuser', )
    search_fields = ('uid', 'name', 'email', )
    list_filter = ('groups', 'user_permissions', )
    exclude = ('password', )
    readonly_fields = ('profile', 'uid', 'name', 'email', 'email_verified', 'last_login')
