# encoding: utf-8

'''🧬🔑🕴️ BioKey user management: views.'''


from ._forgotten import ResetForgottenPasswordForm
from ._ldap import get_account_by_uid, reset_password_in_dit
from ._theme import bootstrap_form_widgets
from .constants import GENERIC_FORM_TEMPLATE
from .models import DirectoryInformationTree
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound, HttpResponseServerError, HttpResponseBadRequest
from django.shortcuts import render
from django.utils import timezone
import logging, datetime


_logger = logging.getLogger(__name__)


def _check(consortium, uid, token) -> HttpResponse | None:
    '''Check the password reset parameters and see if they're valid.

    Returns a `HttpResponse` in case they're invalid, or `None` if they're all OK.
    '''
    dit = DirectoryInformationTree.objects.filter(slug=consortium).first()
    if not dit:
        _logger.warning('reset_password _check: consortium «%s» not found', consortium)
        return HttpResponseNotFound(reason='Consortium unknown')
    account = get_account_by_uid(uid, dit)
    if not account:
        _logger.warning('reset_password _check: account «%s» not found', uid)
        return HttpResponseNotFound(reason='User unknown')
    biokey = account.get('biokey')
    if not biokey:
        _logger.warning('reset_password _check: no biokey for account «%s» in consortium «%s»', uid, consortium)
        return HttpResponseServerError(reason='No biokey')
    reset_token, reset_time = biokey.get('reset_token'), biokey.get('reset_time')
    if not reset_token or not reset_time:
        _logger.warning('reset_password _check: no reset token or reset time for %s in %s', uid, consortium)
        return HttpResponseBadRequest(reason='No reset token or reset time prepared in account')
    now, expiration = timezone.now(), datetime.datetime.fromisoformat(reset_time)
    if now > expiration:
        _logger.warning('reset_password _check: token for %s in %s expired', uid, consortium)
        return HttpResponseBadRequest(reason='Token expired')
    if token != reset_token:
        _logger.warning(
            'reset_password _check: token for %s in %s mismatch; expected %s, got %s', uid, consortium,
            reset_token, token
        )
        return HttpResponseBadRequest(reason='Token mismatch')


def reset_password_form(request: HttpRequest, consortium: str, uid: str, token: str) -> HttpResponse:
    if request.method == 'GET':
        potential_response = _check(consortium, uid, token)
        if potential_response: return potential_response
        form = ResetForgottenPasswordForm(initial={'token': token})
        bootstrap_form_widgets(form)
        title = f'Reset {consortium.upper()} Password'
        return render(request, GENERIC_FORM_TEMPLATE, {'form': form, 'title': title})
    else:
        return HttpResponseBadRequest(reason='GET only')


def reset_password(request: HttpRequest, consortium: str, uid: str) -> HttpResponse:
    if request.method == 'POST':
        form = ResetForgottenPasswordForm(request.POST)
        if form.is_valid():
            dit = DirectoryInformationTree.objects.filter(slug=consortium).first()
            if not dit:
                _logger.warning('reset_password: consortium %s not found', consortium)
                return HttpResponseNotFound(reason='consortium not found')
            reset_password_in_dit(dit, uid, form.cleaned_data['new_password'])
            return render(
                request, 'jpl.edrn.biokey.usermgmt/password-reset-success.html',
                {'uid': uid, 'consortium': consortium.upper()}
            )
        else:
            bootstrap_form_widgets(form)
            title = f'Reset {consortium.upper()} Password'
            return render(request, GENERIC_FORM_TEMPLATE, {'form': form, 'title': title})
    else:
        return HttpResponseBadRequest(reason='not POST')
