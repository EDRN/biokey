# encoding: utf-8

'''🧬🔑🕴️ BioKey user management: LDAP utilities.'''


from ._dits import DirectoryInformationTree
from ._settings import EmailSettings
from .tasks import send_email
from contextlib import contextmanager
from wagtail.models import Site
import logging, ldap, random, re


_logger = logging.getLogger(__name__)
_account_name_total_attempts = 20
_account_name_cleaner = re.compile(r'[^A-Za-z]')
_max_bare_account = 12


@contextmanager
def ldap_connection(dit: DirectoryInformationTree):
    connection = None
    try:
        connection = ldap.initialize(dit.uri)
        connection.simple_bind_s(dit.manager_dn, dit.manager_password)
        yield connection
    finally:
        if connection is not None: del connection


def get_potential_accounts(fn: str, ln: str, dit: DirectoryInformationTree) -> list:
    matches = set()
    with ldap_connection(dit) as connection:
        if not fn:
            results = connection.search_s(dit.user_base, dit.user_scope, f'(sn={ln})')
        else:
            results = connection.search_s(dit.user_base, dit.user_scope, f'(cn={fn} {ln})')
        for match in results:
            matches.add(match[1]['mail'][0].decode('utf-8'))
        matches = list(matches)
        matches.sort()
        return matches


def generate_account_name(fn: str, ln: str, dit: DirectoryInformationTree) -> str:
    _logger.info('Generating a new account name for fn %s and ln %s in %s', fn, ln, dit.title)
    original_uid = f'{fn[0]}{ln}' if fn else ln
    original_uid = re.sub(_account_name_cleaner, '', original_uid)
    original_uid = original_uid[:_max_bare_account].lower()
    uid = original_uid
    attempts = 0

    # Possible race here
    with ldap_connection(dit) as connection:
        while attempts < _account_name_total_attempts:
            results = connection.search_s(dit.user_base, dit.user_scope, f'(uid={uid})')
            if len(results) == 0:
                _logger.info('UID %s is available at present in %s', uid, dit.title)
                return uid
            else:
                uid = f'{uid}{random.randrange(start=100, stop=399, step=1)}'
                attempts += 1
    raise ValueError(f"Tried {attempts} variations on {original_uid} but couldn't find any unusued ones")


def create_public_edrn_account(fn: str, ln: str, telephone: str, email: str, dit: DirectoryInformationTree) -> str:
    _logger.info('Creating public EDRN account for %s at %s', ln, email)
    account_name = generate_account_name(fn, ln, dit)
    settings = EmailSettings.for_site(Site.objects.filter(is_default_site=True).first())
    send_email(
        settings.from_address, [email], 'Your new EDRN account', f'Your account {account_name} is ready', 
        attachment=None, delay=0
    )
    return account_name
