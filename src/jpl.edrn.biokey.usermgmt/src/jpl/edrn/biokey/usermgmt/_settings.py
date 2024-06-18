# encoding: utf-8

'''🧬🔑🕴️ BioKey user management: settings.'''

from django.db import models
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from .constants import MAX_EMAIL_LENGTH


@register_setting
class EmailSettings(BaseSiteSetting):
    from_address = models.EmailField(
        blank=False, null=False, help_text='Address from which to send emails', default='no-reply@jpl.nasa.gov',
        max_length=MAX_EMAIL_LENGTH
    )
    new_users_addresses = models.CharField(
        blank=False, null=False, help_text='Addresses (comma-separated) to notify when new users are created',
        default='ic-accounts@jpl.nasa.gov', max_length=512
    )
    class Meta:
        verbose_name = 'Email'


@register_setting
class PasswordSettings(BaseSiteSetting):
    reset_window = models.IntegerField(
        blank=False, null=False, default=4320,  # 3 days
        help_text='Number of minutes a user has to reset their password after sending the password reset email'
    )
