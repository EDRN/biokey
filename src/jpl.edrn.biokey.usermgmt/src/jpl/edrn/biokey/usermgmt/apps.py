# encoding: utf-8

'''🧬🔑🕴️ BioKey user management: Django application.'''

from django.apps import AppConfig


class BioKeyUserMgmtConfig(AppConfig):
    '''The BioKey user management app.'''
    name = 'jpl.edrn.biokey.usermgmt'
    label = 'jpledrnbiokeyusermgmt'
    verbose_name = 'BioKey user management'
