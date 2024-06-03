# encoding: utf-8

'''🧬🔑🕴️ BioKey user management's filters.'''

from django import template


register = template.Library()


@register.filter
def obscured_email(email: str) -> str:
    at = email.index('@')
    mask = '•' * (at - 2)
    masked_email = email[0] + mask + email[at-1:]
    return masked_email
