# encoding: utf-8

'''🧬🔑🕴️ BioKey user management: change password form.'''

from . import PACKAGE_NAME
from ._forms import AbstractForm, AbstractFormPage
from ._ldap import verify_password
from .constants import MAX_UID_LENGTH, MAX_PASSWORD_LENGTH, GENERIC_FORM_TEMPLATE
from captcha.fields import ReCaptchaField
from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


class PasswordChangeForm(AbstractForm):
    uid = forms.CharField(label='User ID', help_text='Your account name', max_length=MAX_UID_LENGTH)
    current_password = forms.CharField(
        help_text='Your current password', max_length=MAX_PASSWORD_LENGTH, widget=forms.PasswordInput()
    )
    new_password = forms.CharField(
        help_text='New password', max_length=MAX_PASSWORD_LENGTH, widget=forms.PasswordInput()
    )
    confirm_new_password = forms.CharField(
        help_text='Confirm the new password', max_length=MAX_PASSWORD_LENGTH, widget=forms.PasswordInput()
    )
    # 🔮 CAPTCHA?

    def clean(self):
        cleaned_data = super().clean()

        n, c = cleaned_data.get('new_password'), cleaned_data.get('confirm_new_password')
        if n != c: raise ValidationError('New passwords do not match')

        uid, pw = cleaned_data.get('uid'), cleaned_data.get('current_password')
        if not verify_password(self.page.get_parent().specific, uid, pw):
            raise ValidationError('Username and/or password are invalid')

        return cleaned_data


class PasswordChangeFormPage(AbstractFormPage):
    def serve(self, request: HttpRequest) -> HttpResponse:
        if request.method == 'POST':
            form = PasswordChangeForm(request.POST, page=self)
            if form.is_valid():
                dit = self.get_parent().specific
                uid, newpw = form.cleaned_data['uid'], form.cleaned_data['new_password']
                template = dit.change_password(uid, newpw)
                if not template:
                    template = PACKAGE_NAME + '/password-changed.html'
                params = {'page': self, 'uid': uid, 'consortium': dit.slug.upper()}
                return render(request, template, params)
        else:
            form = PasswordChangeForm(page=self)
        self._bootstrap(form)
        return render(request, GENERIC_FORM_TEMPLATE, {'page': self, 'form': form})
