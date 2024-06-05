# encoding: utf-8

'''🧬🔑🕴️ BioKey user management: views.'''


from ._ldap import get_account_by_uid
from .models import DirectoryInformationTree
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound, HttpResponseServerError, HttpResponseBadRequest
from django.utils import timezone
import logging, datetime


_logger = logging.getLogger(__name__)


def reset_password(request: HttpRequest, consortium: str, uid: str, token: str) -> HttpResponse:
    dit = DirectoryInformationTree.objects.filter(slug=consortium).first()
    if not dit:
        _logger.warning('reset_password: consortium «%s» not found', consortium)
        return HttpResponseNotFound(reason='Consortium unknown')
    account = get_account_by_uid(uid, dit)
    if not account:
        _logger.warning('reset_password: account «%s» not found', uid)
        return HttpResponseNotFound(reason='User unknown')
    biokey = account.get('biokey')
    if not biokey:
        _logger.warning('reset_password: no biokey for account «%s» in consortium «%s»', uid, consortium)
        return HttpResponseServerError(reason='No biokey')
    reset_token, reset_time = biokey.get('reset_token'), biokey.get('reset_time')
    if not reset_token or not reset_time:
        _logger.warning('reset_password: no reset token or reset time for %s in %s', uid, consortium)
        return HttpResponseBadRequest(reason='No reset token or reset time prepared in account')
    now, expiration = timezone.now(), datetime.datetime.fromisoformat(reset_time)
    if now > expiration:
        _logger.warning('reset_password: token for %s in %s expired', uid, consortium)
        return HttpResponseBadRequest(reason='Token expired')
    if token != reset_token:
        _logger.warning(
            'reset_password: token for %s in %s mismatch; expected %s, got %s', uid, consortium,
            reset_token, token
        )
        return HttpResponseBadRequest(reason='Token mismatch')

    raise NotImplementedError('not working yet')
