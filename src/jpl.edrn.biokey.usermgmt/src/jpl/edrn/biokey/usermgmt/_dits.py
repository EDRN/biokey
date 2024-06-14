# encoding: utf-8

'''🧬🔑🕴️ BioKey user management: directory information trees.

Note: we cannot import ._ldap up top here as it'll result in a circular dependency.
'''

from . import PACKAGE_NAME
from ._paths import make_pwreset_url
from ._settings import EmailSettings, PasswordSettings
from .constants import MAX_EMAIL_LENGTH
from .tasks import send_email
from django import forms
from django.core.validators import URLValidator
from django.db import models
from django.http import HttpRequest
from django.utils import timezone
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, FieldRowPanel
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
    _requested_reset = '''Hello!

Someone, perhaps you, requested a reset of the password for the account "{uid}".

To reset the password for account "{uid}", you'll need to visit the following link within {natural_delta}:

{link}

Please note that link will expire on {expiration_time} (UTC). If you can't visit the link in that time, simply return to {url} and restart the forgotten password process.

Note that if you did not request to reset the password, then simply ignore this email.

Thank you.
'''
    _created_account = '''Hello!

Your account, "{uid}", has been created for the {consortium}. To set the password for this account, you'll need to visit the following link within {natural_delta}:

{link}

Please note that this link will expire on {expiration_time} (UTC). If you can't visit the link in that time, visit {url} and choose the "Forgotten password" option for a fresh link.

Thank you.
'''

    _requested_uid = '''Hello!

Someone, perhaps you, asked for the username for the {consortium} account that goes with this email address.

The username is: {uid}

You can visit {url} to change the password for "{uid}" (if you know it), or reset the password (if forgotten).

Note that if you did not request this, then simply ignore this email.

Thank you.
'''

    template = PACKAGE_NAME + '/dit.html'
    page_description = 'A single data information tree within LDAP in which users and groups are found'
    search_auto_update = False

    page_title = models.CharField(
        blank=False, null=False, default='Page title', max_length=255, help_text='Title to put at the top of the page'
    )
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
    creation_email_template = models.TextField(
        blank=False, help_text="Email template for end users' newly-created accounts", default=_created_account
    )
    reset_request_email_template = models.TextField(
        blank=False, help_text="Email template for end users' requests to reset their passwords",
        default=_requested_reset
    )
    forgotten_uid_template = models.TextField(
        blank=False, help_text="Email template for end users' to recover forgotten usernames, not forgotten passwords",
        default=_requested_uid
    )
    help_address = models.EmailField(
        blank=False, max_length=MAX_EMAIL_LENGTH, help_text='Email address if users need help',
        default='help@email.address',
    )
    logo = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='dit_logo'
    )

    content_panels = Page.content_panels + [
        FieldPanel('page_title'),
        FieldPanel('logo'),
        FieldPanel('uri'),
        MultiFieldPanel(heading='LDAP Manager', children=(
            FieldRowPanel(children=(
                FieldPanel('manager_dn'),
                FieldPanel('manager_password', widget=forms.PasswordInput),
            )),
        )),
        MultiFieldPanel(heading='Bases and Scopes', children=(
            FieldRowPanel((
                FieldPanel('user_base'),
                FieldPanel('user_scope'),
            )),
            FieldRowPanel((
                FieldPanel('group_base'),
                FieldPanel('group_scope'),
            )),
        )),
        FieldPanel('help_address'),
        FieldPanel('creation_email_template'),
        FieldPanel('reset_request_email_template'),
        FieldPanel('forgotten_uid_template'),
    ]

    def get_context(self, request: HttpRequest, *args, **kwargs) -> dict:
        context = super().get_context(request, args, kwargs)
        context['is_superuser'] = request.user.is_superuser
        context['user_scope'] = _scope_choices[self.user_scope]
        context['group_scope'] = _scope_choices[self.group_scope]
        sign_up = self.get_children().filter(slug='sign-up').first()
        if sign_up: context['sign_up'] = sign_up.url
        changepw = self.get_children().filter(slug='change-password').first()
        if changepw: context['changepw'] = changepw.url
        forgotten = self.get_children().filter(slug='forgotten').first()
        if forgotten: context['forgotten'] = forgotten.url
        return context

    def send_reset_email(self, account: dict, request: HttpRequest):
        # Generate a timer and a token
        site = Site.find_for_request(request)
        email, pwd = EmailSettings.for_site(site), PasswordSettings.for_site(site)
        window, now = datetime.timedelta(minutes=pwd.reset_window), timezone.now()
        expiration = now + window
        from ._ldap import generate_reset_token
        token = generate_reset_token(account, expiration, self)
        link = make_pwreset_url(self.slug, account['uid'], token, request)
        message = self.reset_request_email_template.format(
            uid=account['uid'], natural_delta=humanize.naturaldelta(window), link=link, 
            expiration_time=expiration.ctime(), url=self.full_url,
        )
        send_email(
            email.from_address, [account['email']], f'Password reset for {account["uid"]}', message,
            attachment=None, delay=0
        )

    def send_account_reminder_email(self, account: dict):
        raise NotImplementedError("This doesn't work yet either")

    def create_account(self, fn: str, ln: str, phone: str, email: str, request: HttpRequest) -> str:
        from ._ldap import create_new_account, generate_reset_token, get_account_by_uid
        site = Site.find_for_request(request)
        account_name = create_new_account(fn, ln, phone, email, self)
        account = get_account_by_uid(account_name, self)
        email_settings, pwd_settings = EmailSettings.for_site(site), PasswordSettings.for_site(site)
        window, now = datetime.timedelta(minutes=pwd_settings.reset_window), timezone.now()
        expiration = now + window
        consortium = self.slug.upper()
        token = generate_reset_token(account, expiration, self)
        link = make_pwreset_url(self.slug, account_name, token, request)
        message = self.creation_email_template.format(
            uid=account_name, consortium=self.title, natural_delta=humanize.naturaldelta(window), link=link,
            expiration_time=expiration.ctime(), url=self.full_url
        )
        send_email(
            email_settings.from_address, [email], f'Your new {consortium} account', message, attachment=None, delay=0
        )
        send_email(
            email_settings.from_address, [i.strip() for i in email_settings.new_users_addresses.split(',')],
            f'New {consortium} account created', f'New {consortium} account «{account_name}» has just been created',
            attachment=None, delay=10
        )
        return account_name

    def send_uid_reminders(self, accounts: list[dict], request: HttpRequest):
        delay, consortium, settings = 0, self.slug.upper(), EmailSettings.for_site(Site.find_for_request(request))
        subject = f'Your {consortium} account username'
        for account in accounts:
            email, uid = account['email'], account['uid']
            message = self.forgotten_uid_template.format(consortium=consortium, url=self.full_url, uid=uid)
            send_email(settings.from_address, [email], subject, message, attachment=None, delay=delay)
            delay += 2

    def change_password(self, uid: str, new_password: str) -> str | None:
        '''Change the password for `uid` to `new_password`.

        Return None if it worked, or a string message if it didn't. This implementation
        always returns None.
        '''
        from ._ldap import change_password
        change_password(self, uid, new_password)
        return None


class EDRNDirectoryInformationTree(DirectoryInformationTree):
    page_description = 'A data information tree with users backed by the DMCC'
    template = PACKAGE_NAME + '/dit.html'

    _dmcc_reset = '''Your account, "{uid}", is managed the Data Management and Coordinating Center (DMCC) of the Early Detection Research Network.

To reset the password on this account, please visit the DMCC website at this address:

https://www.compass.fhcrc.org/edrns/pub/user/resetPwd.aspx?t=pwd&amp;t2=pwd2&amp;sub=form&amp;w=1&amp;p=3&amp;param=reset&amp;t3=pwd&amp;sub2=lift

Thank you.
'''

    dmcc_managed_email_template = models.TextField(
        blank=True, help_text='Email template to notify that theirs is a secure-site account', default=_dmcc_reset
    )

    content_panels = DirectoryInformationTree.content_panels + [
        FieldPanel('dmcc_managed_email_template'),
    ]

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
            message = self.dmcc_managed_email_template.format(uid=account['uid'])
            send_email(settings.from_address, [to_address], 'EDRN Password Reset', message, attachment=None, delay=0)
        else:
            # It's one of "our own"
            super().send_reset_email(account, request)

    def change_password(self, uid: str, new_password: str) -> str | None:
        from ._ldap import get_account_by_uid
        account = get_account_by_uid(uid, self)
        if account.get('desc', '').startswith('imported via EDRN dmccsync'):
            return PACKAGE_NAME + '/dmcc-password-change-required.html'
        return super().change_password(uid, new_password)
