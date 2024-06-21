# encoding: utf-8

'''🧬🔑🕴️ BioKey user management's filters.'''

from datetime import datetime
from django import template
import humanize

register = template.Library()


@register.filter
def obscured_email(email: str) -> str:
    at = email.index('@')
    mask = '•' * (at - 2)
    masked_email = email[0] + mask + email[at-1:]
    return masked_email


@register.filter
def waiting_since(created_at: datetime) -> str:
    return humanize.naturaltime(created_at)


@register.filter
def datetime_iso8601(created_at: datetime) -> str:
    return created_at.isoformat()
