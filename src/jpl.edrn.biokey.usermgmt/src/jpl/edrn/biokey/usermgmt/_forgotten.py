# encoding: utf-8

'''🧬🔑🕴️ BioKey user management: forgotten details form.'''


from ._forms import AbstractForm, AbstractFormPage
from ._ldap import get_potential_accounts, create_public_edrn_account
from captcha.fields import ReCaptchaField
from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


class ForgottenDetailsForm(AbstractForm):
    _uid_help = '''If you remember your user ID, fill it in and we'll email you a link to reset your password. If you can't remember it, fill in your email address below instead.'''
    uid = forms.CharField(label='User ID', required=False, help_text=_uid_help)
    email = forms.EmailField(
        label='Email', required=False,
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
                breakpoint()
        else:
            form = ForgottenDetailsForm(page=self)
        self._bootstrap(form)
        return render(request, 'jpl.edrn.biokey.usermgmt/form.html', {'page': self, 'form': form})
