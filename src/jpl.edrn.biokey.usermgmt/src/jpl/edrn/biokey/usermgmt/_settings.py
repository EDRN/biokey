# encoding: utf-8

'''🧬🔑🕴️ BioKey user management: settings.'''

from django.db import models
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


@register_setting
class EmailSettings(BaseSiteSetting):
    from_address = models.EmailField(
        blank=False, null=False, help_text='Address from which to send emails', default='no-reply@jpl.nasa.gov',
        max_length=50
    )
    class Meta:
        verbose_name = 'Email'
