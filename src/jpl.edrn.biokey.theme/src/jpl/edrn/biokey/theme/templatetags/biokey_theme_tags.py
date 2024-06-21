# encoding: utf-8

'''🧬🔑🎨 Biokey: look/feel/skin/theme's tags.'''

from django import template
from django.template.context import Context
from django.urls import reverse
from django.utils.safestring import mark_safe
from importlib import import_module
from jpl.edrn.biokey.theme import PACKAGE_NAME
from jpl.edrn.biokey.theme.models import ColophonSettings
from wagtail.models import Site

register = template.Library()


@register.simple_tag(takes_context=False)
def biokey_site_version() -> str:
    version = None
    try:
        module = import_module('edrnsite.policy')  # No circular dependency here
        version = getattr(module, 'VERSION', None)
    except ModuleNotFoundError:
        pass
    if not version:
        # Okay, just use the theme's version
        from jpl.edrn.biokey.theme import VERSION as version
    return mark_safe(str(version))


@register.inclusion_tag(PACKAGE_NAME + '/colophon.html', takes_context=True)
def biokey_colophon(context: Context) -> dict:
    settings = ColophonSettings.for_site(Site.find_for_request(context['request']))
    params = {'webmaster': settings.webmaster, 'manager': settings.site_honcho, 'clearance': settings.clearance}
    request = context['request']
    if request.user.is_anonymous:
        params['login'] = True
        params['url'] = f'{reverse("wagtailcore_login")}?next={request.path}'
    else:
        params['login'] = False
        params['url'] = f'{reverse("logout")}?next={request.path}'
        params['uid'] = request.user.username
        params['permissions'] = request.user.is_staff or request.user.is_superuser
    return params
