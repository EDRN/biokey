# encoding: utf-8

'''🧬🔑🕴️ BioKey user management: forgotten details form.'''


from . import PACKAGE_NAME
from ._forms import AbstractForm, AbstractFormPage
from ._ldap import get_account_by_uid, get_accounts_by_email
from .constants import MAX_UID_LENGTH, MAX_EMAIL_LENGTH, MAX_PASSWORD_LENGTH, GENERIC_FORM_TEMPLATE
from captcha.fields import ReCaptchaField
from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


class ForgottenDetailsForm(AbstractForm):
    _uid_help = '''If you remember your user ID, fill it in and we'll email you a link to reset your password. If you can't remember it, fill in your email address below instead.'''
    uid = forms.CharField(label='User ID', required=False, help_text=_uid_help, max_length=MAX_UID_LENGTH)
    email = forms.EmailField(
        label='Email', required=False, max_length=MAX_EMAIL_LENGTH,
        help_text="Can't remember your user ID? Fill in your email address instead and we'll email your user ID to you."
    )
    # 🔮 CAPTCHA?

    def clean(self):
        cleaned_data = super().clean()

        u, e = cleaned_data.get('uid'), cleaned_data.get('email')
        if not u and not e:
            raise ValidationError('Please fill in either your user ID or your email address.')
        elif u and e:
            raise ValidationError('Please fill in only your user ID or only your email address—not both.')
        return cleaned_data


class ForgottenDetailsFormPage(AbstractFormPage):
    def serve(self, request: HttpRequest) -> HttpResponse:
        if request.method == 'POST':
            form = ForgottenDetailsForm(request.POST, page=self)
            if form.is_valid():
                dit = self.get_parent().specific
                uid, email = form.cleaned_data['uid'], form.cleaned_data['email']
                if uid:
                    account = get_account_by_uid(uid, dit)
                    # If account is found or not, tell the user the process has begun anyway; this
                    # prevents information leakage about which are known account names.
                    params = {'page': self, 'uid': uid, 'us': dit.help_address}
                    if account:
                        dit.send_reset_email(account, request)
                    return render(request, PACKAGE_NAME + '/password-reset-email-sent.html', params)
                elif email:
                    accounts = get_accounts_by_email(email, dit)
                    # If accounts are found or not, tell the user we've sent the reminders by email.
                    # As with the `uid` case, this prevents the leakage of known email addresses.
                    dit.send_uid_reminders(accounts, request)
                    params = {'page': self, 'email': email, 'dit': dit}
                    return render(request, PACKAGE_NAME + '/uid-reminder-email-sent.html', params)
        else:
            form = ForgottenDetailsForm(page=self)
        self._bootstrap(form)
        return render(request, GENERIC_FORM_TEMPLATE, {'page': self, 'form': form})


class ResetForgottenPasswordForm(AbstractForm):
    new_password = forms.CharField(
        help_text='Enter a new password', max_length=MAX_PASSWORD_LENGTH, widget=forms.PasswordInput()
    )
    confirm_new_password = forms.CharField(
        help_text='Confirm the new password', max_length=MAX_PASSWORD_LENGTH, widget=forms.PasswordInput()
    )

    def clean(self):
        cleaned_data = super().clean()
        n, c = cleaned_data.get('new_password'), cleaned_data.get('confirm_new_password')
        if n != c: raise ValidationError('Passwords do not match')
        return cleaned_data
