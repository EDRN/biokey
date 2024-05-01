# encoding: utf-8

'''🧬🔑🦦 BioKey content: settings.'''


# Migration Modules
#
# This shouldn't be necessary, but I am seeing the generated migrations code end up in the virtual
# environment and not in the source tree when running `makemigrations` 🤨
#
# 🔗 https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules

MIGRATION_MODULES = {
    'jpl.edrn.biokey.content': 'jpl.edrn.biokey.content.migrations'
}


# Installed Applications
# ----------------------
#
# The "apps" (Python packages) enabled for Django.
#
# 🔗 https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps

INSTALLED_APPS = [
    'jpl.edrn.biokey.streams',
    # 'wagtail.contrib.table_block',
    # 'wagtail.contrib.typed_table_block',
    # 'wagtail.contrib.forms',
    'widget_tweaks',
    # 'wagtailcaptcha',
    # 'captcha',
]
