# encoding: utf-8

'''🧬🔑 BioKey site policy.'''

from django.apps import AppConfig


class BioKeyPolicyConfig(AppConfig):
    '''The BioKey policy app.'''
    name = 'jpl.edrn.biokey.policy'
    label = 'jpledrnbiokeypolicy'
    verbose_name = 'BioKey Policy'
