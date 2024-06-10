# encoding: utf-8

'''🧬🔑🕴️ BioKey user management: settings.'''

from . import PACKAGE_NAME


# Migration Modules
#
# This shouldn't be necessary, but I am seeing the generated migrations code end up in the virtual
# environment and not in the source tree when running `makemigrations` 🤨
#
# 🔗 https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules

MIGRATION_MODULES = {
    PACKAGE_NAME: PACKAGE_NAME + '.migrations'
}
