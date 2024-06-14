# encoding: utf-8

'''🧬🔑🎨 Biokey: look/feel/skin/theme: Django app.'''

from . import PACKAGE_NAME
from django.apps import AppConfig


class BioKeyThemeConfig(AppConfig):
    '''BioKey theme app.'''
    name = PACKAGE_NAME
    label = PACKAGE_NAME.replace('.', '')
    verbose_name = 'BioKey Theme'
