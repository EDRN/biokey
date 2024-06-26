# encoding: utf-8

'''🧬🔑🎨 Biokey: look/feel/skin/theme: settings.'''

from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


@register_setting
class ColophonSettings(BaseSiteSetting):
    site_honcho = models.CharField(
        blank=False, null=False, help_text='JPL cognizant person who manages the site', default='Dan Crichton'
    )
    webmaster = models.CharField(
        blank=False, null=False, help_text='JPL cognizant person who masters the site', default='Rojeh Yaghoobi'
    )
    clearance = models.CharField(blank=False, null=False, help_text='JPL clearance number', default='CL № 22-6220')

    panels = [
        FieldPanel('site_honcho'), FieldPanel('webmaster'), FieldPanel('clearance')
    ]
