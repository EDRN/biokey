# encoding: utf-8

'''🧬🔑🕴️ BioKey user management: directory information trees.'''

from django.db import models
from django import forms
from django.core.validators import URLValidator
from django.http import HttpRequest
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page
import ldap


_scope_choices = {
    ldap.SCOPE_BASE: 'base',
    ldap.SCOPE_ONELEVEL: 'one-level',
    ldap.SCOPE_SUBTREE: 'subtree',
}


class DirectoryInformationTree(Page):
    template = 'jpl.edrn.biokey.usermgmt/dit.html'
    page_description = 'A single data information tree within LDAP in which users and groups are found'
    search_auto_update = False

    uri = models.CharField(
        blank=False, max_length=200, help_text='URI to the LDAP server as an "ldap:" or "ldaps: URL',
        validators=[URLValidator(schemes=['ldap', 'ldaps'])]
    )
    manager_dn = models.CharField(
        blank=False, max_length=200, help_text='DN of the manager of the server', default='uid=admin,ou=system'
    )
    manager_password = models.CharField(
        blank=False, max_length=80, help_text='Password of manager DN', default='password'
    )
    user_base = models.CharField(
        blank=False, max_length=600, help_text='Base DN where to find users', default='ou=users,o=organization'
    )
    user_scope = models.IntegerField(
        blank=False, help_text='Search scope for users', default=ldap.SCOPE_ONELEVEL, choices=_scope_choices.items()
    )
    group_base = models.CharField(
        blank=False, max_length=600, help_text='Base DN where to find groups', default='ou=groups,o=organization'
    )
    group_scope = models.IntegerField(
        blank=False, help_text='Search scope for groups', default=ldap.SCOPE_ONELEVEL, choices=_scope_choices.items()
    )

    content_panels = Page.content_panels + [
        FieldPanel('uri'),
        FieldPanel('manager_dn'),
        FieldPanel('manager_password', widget=forms.PasswordInput),
        FieldPanel('user_base'),
        FieldPanel('user_scope'),
        FieldPanel('group_base'),
        FieldPanel('group_scope'),
    ]

    def get_context(self, request: HttpRequest, *args, **kwargs) -> dict:
        context = super().get_context(request, args, kwargs)
        context['is_superuser'] = request.user.is_superuser
        context['user_scope'] = _scope_choices[self.user_scope]
        context['group_scope'] = _scope_choices[self.group_scope]
        sign_up = self.get_children().filter(slug='sign-up').first()
        if sign_up: context['sign_up'] = sign_up.url
        forgotten = self.get_children().filter(slug='forgotten').first()
        if forgotten: context['forgotten'] = forgotten.url
        return context


class EDRNDirectoryInformationTree(DirectoryInformationTree):
    page_description = 'A data information tree with users backed by the DMCC'
    template = 'jpl.edrn.biokey.usermgmt/dit.html'
