# encoding: utf-8

'''🧬🔑🦦 BioKey streams: Django application.'''

from django.apps import AppConfig


class BioKeyStreamsConfig(AppConfig):
    '''The BioKey streams app.'''
    name = 'jpl.edrn.biokey.streams'
    label = 'jpledrnbiokeystreams'
    verbose_name = 'BioKey streams'
