# encoding: utf-8

'''🧬🔑🕴️ BioKey user management: sign-up forms.'''


from django import forms

from django.http import HttpRequest, HttpResponse
from captcha.fields import ReCaptchaField
from ._forms import AbstractForm, AbstractFormPage
from django.shortcuts import render
from ._ldap import get_potential_accounts, create_public_edrn_account


class NameRequestForm(AbstractForm):
    first_name = forms.CharField(
        label='First Name', required=False,
        help_text="What's your first name? Sometimes this is called your given name or forename.", 
    )
    last_name = forms.CharField(label='Last Name', help_text="What's your last name, surname, or family name?")
    do_sign_up = forms.CharField(initial='0', widget=forms.HiddenInput(), required=False)


class AccountSignUpForm(NameRequestForm):
    _certification_text = '''By checking this box, I certify that I'm signing up for this account for my own use and I am authorized to do so.'''
    _telephone_text = '''Your telephone number, including country code and area code, if you know them. We use this as a last resort to text you a new password should other password resets fail.'''

    telephone = forms.CharField(label='Telephone', max_length=40, help_text=_telephone_text)
    email = forms.EmailField(label='Email', help_text='How to reach you by email.')
    for_self = forms.BooleanField(label='Certification', help_text=_certification_text)

    do_sign_up = forms.CharField(initial='1', widget=forms.HiddenInput(), required=False)

    # 🔮 CAPTCHA needed here
    # if not settings.DEBUG:
    #     captcha = ReCaptchaField()


class NameRequestFormPage(AbstractFormPage):
    def serve(self, request: HttpRequest) -> HttpResponse:
        if request.method == 'POST':
            form, parent, dit = NameRequestForm(request.POST, page=self), self.get_parent(), self.get_parent().specific
            if form.is_valid():
                do_sign_up = form.cleaned_data.get('do_sign_up') == '1'
                if do_sign_up:
                    form = AccountSignUpForm(request.POST, page=self)
                    if form.is_valid() and form.cleaned_data.get('for_self'):
                        account_name = create_public_edrn_account(
                            form.cleaned_data['first_name'], form.cleaned_data['last_name'],
                            form.cleaned_data['telephone'], form.cleaned_data['email'], dit
                        )
                        params = {
                            'email': form.cleaned_data['email'], 'account_name': account_name,
                            'parent_url': parent.url, 'consortium': parent.title
                        }
                        return render(request, 'jpl.edrn.biokey.usermgmt/account-created.html', params)
                else:
                    fn, ln = form.cleaned_data['first_name'], form.cleaned_data['last_name']
                    potential_emails = get_potential_accounts(fn, ln, dit)

                    # Possible existing account
                    if len(potential_emails) > 0:
                        plural = len(potential_emails) > 1
                        params = {
                            'potential_emails': potential_emails, 'plural': plural, 'consortium': parent.title,
                            'parent_url': parent.url, 'first_name': fn, 'last_name': ln
                        }
                        return render(request, 'jpl.edrn.biokey.usermgmt/potential-emails.html', params)
                    else:
                        form = AccountSignUpForm(initial={'first_name': fn, 'last_name': ln}, page=self)

            # Else pass through to render default

        else:
            # First visit via GET, so just ask for name
            form = NameRequestForm(page=self)
        self._bootstrap(form)
        return render(request, 'jpl.edrn.biokey.usermgmt/form.html', {'page': self, 'form': form})
