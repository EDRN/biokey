# encoding: utf-8

'''🧬🔑🕴️ BioKey user management: Django application.'''

from . import PACKAGE_NAME
from django.apps import AppConfig


class BioKeyUserMgmtConfig(AppConfig):
    '''The BioKey user management app.'''
    name = PACKAGE_NAME
    label = 'jpledrnbiokeyusermgmt'
    verbose_name = 'BioKey user management'
