# encoding: utf-8

'''🚀👢🎨 Quick and dirty Bootstrap theme: settings.'''


# Installed Applications
# ----------------------
#
# The "apps" (Python packages) enabled for Django.
#
# 🔗 https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps

INSTALLED_APPS = []


# Migration Modules
#
# This shouldn't be necessary, but I am seeing the generated migrations code end up in the virtual
# environment and not in the source tree when running `makemigrations` 🤨
#
# 🔗 https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules

MIGRATION_MODULES = {
    'jpl.wagtail.bootstrap': 'jpl.wagtail.bootstrap.migrations'
}


# Templates
# ---------
#
# The template engines and getting them going, etc.
#
# 🔗 https://docs.djangoproject.com/en/dev/ref/settings/#templates

# This isn't necessary since the user of this package probably has a TEMPLATES with
# APP_DIRS = True and as a result picks up every possible template dir.
# 
# TEMPLATES = [
#     {
#         'NAME': 'jpl.wagtail.bootstrap',
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',

#             ],
#         },
#     },
# ]

TEMPLATES = []
