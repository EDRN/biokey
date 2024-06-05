# encoding: utf-8

'''🧬🔑🕴️ BioKey user management: directory information trees.

Note: we cannot import ._ldap up top here as it'll result in a circular dependency.
'''

from ._settings import EmailSettings, PasswordSettings
from ._paths import make_pwreset_url
from .tasks import send_email
from django import forms
from django.core.validators import URLValidator
from django.db import models
from django.http import HttpRequest
from django.utils import timezone
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page
from wagtail.models import Site
import ldap, logging, humanize, datetime


_logger = logging.getLogger(__name__)

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

    _biokey_reset = '''To reset the password for account "{uid}", you'll need to visit the following link within {natural_delta}:

{link}

Please note that link will expire on {expiration_time} (UTC). If you can't visit the link in that time, simply return to {url} and restart the forgotten password process.

Thank you.
'''

    def send_reset_email(self, account: dict, request: HttpRequest):
        # Generate a timer and a token
        site = Site.objects.filter(is_default_site=True).first()
        email, pwd = EmailSettings.for_site(site), PasswordSettings.for_site(site)
        window, now = datetime.timedelta(minutes=pwd.reset_window), timezone.now()
        expiration = now + window
        from ._ldap import generate_reset_token
        token = generate_reset_token(account, expiration, self)
        link = make_pwreset_url(self.slug, account['uid'], token, request)
        message = self._biokey_reset.format(
            uid=account['uid'], natural_delta=humanize.naturaldelta(window), link=link, 
            expiration_time=expiration.ctime(), url=self.full_url,
        )
        send_email(
            email.from_address, [account['email']], f'Password reset for {account["uid"]}', message,
            attachment=None, delay=0
        )

    def send_account_reminder_email(self, account: dict):
        raise NotImplementedError("This doesn't work yet either")


class EDRNDirectoryInformationTree(DirectoryInformationTree):
    page_description = 'A data information tree with users backed by the DMCC'
    template = 'jpl.edrn.biokey.usermgmt/dit.html'

    _dmcc_reset = '''Your account, "{uid}" is managed the Data Management and Coordinating Center (DMCC) of the Early Detection Research Network.

To reset the password on this account, please visit the DMCC website at this address:

https://www.compass.fhcrc.org/edrns/pub/user/resetPwd.aspx?t=pwd&amp;sub=form&amp;w=1&amp;p=3&amp;param=reset&amp;t3=982

Thank you.
'''

    def send_reset_email(self, account: dict, request: HttpRequest):
        '''Send a password reset email for EDRN.

        If it's a "secure" site account, send the message that directs people to 
        the DMCC. Otherwise, direct them to our own reset.
        '''

        settings = EmailSettings.for_site(Site.objects.filter(is_default_site=True).first())
        to_address = account.get('email')
        if not to_address:
            _logger.warning('EDRN reset email for account % has no email address; skipping sending', account)
            return

        # If it's a DMCC account, let the DMCC handle it
        if account.get('desc', '').startswith('imported via EDRN dmccsync'):
            message = self._dmcc_reset.format(uid=account['uid'])
            send_email(settings.from_address, [to_address], 'EDRN Password Reset', message, attachment=None, delay=0)
        else:
            # It's one of "our own"
            super().send_reset_email(account, request)
