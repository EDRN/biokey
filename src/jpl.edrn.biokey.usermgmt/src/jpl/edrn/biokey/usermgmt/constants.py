# encoding: utf-8

'''🧬🔑🕴️ BioKey user management: constants.'''

from . import PACKAGE_NAME


# Max UID length, must be at least 4 to account for random 3 digits
MAX_UID_LENGTH = 15

# How long an email address can be
MAX_EMAIL_LENGTH = 50

# How long a password can be
MAX_PASSWORD_LENGTH = 250

# Name of the template that renders forms
GENERIC_FORM_TEMPLATE = PACKAGE_NAME + '/form.html'

# Max length of a string telephone number
MAX_PHONE_LENGTH = 40
