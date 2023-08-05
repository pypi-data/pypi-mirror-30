from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres import fields


class A0UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, uid, email, password, **extra_fields):
        """
        Create and save a user with the given uid, email, and password.
        """
        if not uid:
            raise ValueError('The given uid must be set')
        email = self.normalize_email(email)
        uid = self.model.normalize_username(uid)
        user = self.model(uid=uid, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, uid, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(uid, email, password, **extra_fields)

    def create_superuser(self, uid, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(uid, email, password, **extra_fields)


class A0User(AbstractBaseUser, PermissionsMixin):
    """
    The user model. Relies on JSONField to store the full user profile.
    @uid: Auth0 user_id
    @name: User's name
    @email: User's email
    """
    uid = models.CharField(_('auth0 user id'), max_length=140, null=False, db_index=True, unique=True)
    name = models.CharField(_('name'), max_length=140, null=True, blank=True)
    email = models.EmailField(_('email address'), max_length=140, null=False, blank=False)
    email_verified = models.BooleanField(_('email verified'), default=False)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    profile = fields.JSONField(_('user profile'), null=True)

    objects = A0UserManager()

    USERNAME_FIELD = 'uid'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name
