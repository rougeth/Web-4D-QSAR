from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin


class EmailUserManager(BaseUserManager):
    def create_user(self, *args, **kwargs):
        email = kwargs["email"]
        email = self.normalize_email(email)
        password = kwargs["password"]
        kwargs.pop("password")

        if not email:
            raise ValueError(_('Users must have an email address'))

        user = self.model(**kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, *args, **kwargs):
        user = self.create_user(**kwargs)
        user.is_superuser = True
        user.save(using=self._db)
        return user


class MyUser(PermissionsMixin, AbstractBaseUser):
    email = models.EmailField(
        verbose_name=_('Email address'),
        unique=True,
    )
    first_name = models.CharField(
        verbose_name=_('Name'),
        max_length=50,
        blank=False,
        help_text=_('Inform your name'),
    )
    last_name = models.CharField(
        verbose_name=_('Surname'),
        max_length=50,
        blank=False,
        help_text=_('Inform your last name'),
    )
    endereco = models.CharField(max_length=100, default='',blank=True)
    USERNAME_FIELD = 'email'
    objects = EmailUserManager()
