# encoding: utf-8

'''🧬🔑🕴️ BioKey user management: LDAP utilities.'''


from ._dits import DirectoryInformationTree
from .constants import MAX_EMAIL_LENGTH
from contextlib import contextmanager
import logging, ldap, random, re, string, hashlib, base64, ldap.modlist, json, datetime, os


_logger = logging.getLogger(__name__)

_account_name_cleaner        = re.compile(r'[^A-Za-z]')
_account_name_total_attempts = 20
_biokey_json_re              = re.compile(r'([^@]*)(@@biokey=(.*$))?')
_edrn_object_classes         = ['top', 'person', 'organizationalPerson', 'inetOrgPerson', 'edrnPerson']
_max_bare_account            = max(MAX_EMAIL_LENGTH - 3, 4)
_random_password_corpus      = string.ascii_letters + string.digits
_random_password_length      = 20
_reset_token_random_bytes    = 32
_reset_token_length          = 16


def _ldap_to_dict(search_result: tuple) -> dict:
    '''Convert an LDAP search result into a dict.

    LDAP search result is a tuple of (string DN and dict of byte-encoded attributes).
    Convert the byte-encoded attributes into UTF-8 strings and return that dict, adding
    the DN to it. Simplify some of the attribute names too. This makes many assumptions
    about our user schema. Leave out the password.

    If the `@@biokey` string is found in the description, parse it as json and return
    its dict representation in the `biokey` key.
    '''
    dn, d = search_result
    desc = d['description'][0].decode('utf-8')
    biokey_match, biokey = _biokey_json_re.match(desc), None
    if biokey_match and biokey_match.group(3):
        try:
            biokey = json.loads(biokey_match.group(3))
        except json.JSONDecodeError as ex:
            _logger.warning('Corrupted biokey json in %s: %s', dn, ex.msg)
    else:
        biokey = {}
    attributes = {
        'dn': dn,
        'email': d['mail'][0].decode('utf-8'),
        'sn': d['sn'][0].decode('utf-8'),
        'cn': d['cn'][0].decode('utf-8'),
        'desc': desc,
        'uid': d['uid'][0].decode('utf-8'),
    }
    if 'telephoneNumber' in d:
        attributes['phone'] = d['telephoneNumber'][0].decode('utf-8')
    if 'biokey':
        attributes['biokey'] = biokey
    return attributes


@contextmanager
def ldap_connection(dit: DirectoryInformationTree):
    connection = None
    try:
        connection = ldap.initialize(dit.uri)
        connection.simple_bind_s(dit.manager_dn, dit.manager_password)
        yield connection
    finally:
        if connection is not None: del connection


def _hash_password(password: str) -> bytes:
    '''Hash the given `password` using SHA and encoded into bytes suitable for LDAP.'''
    hasher = hashlib.new('sha1', password.encode('utf-8'))
    hashed_password = '{SHA}' + base64.b64encode(hasher.digest()).decode('ascii')
    return hashed_password.encode('utf-8')


def generate_random_ldap_password() -> bytes:
    # What I used in lpdautils:
    pw = ''.join(random.sample(_random_password_corpus, _random_password_length))
    # What I originally came up with:
    # pw = ''.join(random.choices(_random_password_corpus, k=_random_password_length)).encode('utf-8')
    return _hash_password(pw)


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


def create_account(
    uid: str, fn: str, ln: str, email: str, phone: str, ocs: list[str], consortium: str, dit: DirectoryInformationTree
):
    dn = f'uid={uid},{dit.user_base}'
    cn = f'{fn} {ln}' if fn else ln
    description = f'@@biokey={json.dumps({"consortium": consortium})}'.encode('utf-8')
    attrs = {
        'uid': uid.encode('utf-8'),
        'sn': ln.encode('utf-8'),
        'cn': cn.encode('utf-8'),
        'mail': email.encode('utf-8'),
        'userPassword': generate_random_ldap_password(),
        'objectClass': [i.encode('utf-8') for i in ocs],
        'description': [description]
    }
    if phone:
        attrs['telephoneNumber'] = phone.encode('utf-8')
    modlist = ldap.modlist.addModlist(attrs)
    with ldap_connection(dit) as connection:
        _logger.info('Creating user «%s»', dn)
        connection.add_s(dn, modlist)


def generate_account_name(fn: str, ln: str, dit: DirectoryInformationTree) -> str:
    _logger.info('Generating a new account name for fn «%s» and ln «%s» in «%s»', fn, ln, dit.title)
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
                _logger.info('UID «%s» is current;y available in «%s»', uid, dit.title)
                return uid
            else:
                uid = f'{uid}{random.randrange(start=100, stop=399, step=1)}'
                attempts += 1
    raise ValueError(f"Tried {attempts} variations on {original_uid} but couldn't find any unusued ones")


def _update_biokey_description(account: dict, biokey: dict):
    '''Update the `@@biokey` in the description of the given `account`.

    This preserves any text preceding the `@@biokey`. It'll encode it as UTF-8 too.
    '''
    biokey_match = _biokey_json_re.match(account.get('description', ''))
    preceding = biokey_match.group(1) if biokey_match else ''
    return f'{preceding} @@biokey={json.dumps(biokey)}'.strip().encode('utf-8')


def generate_reset_token(account: dict, expiration: datetime.datetime, dit: DirectoryInformationTree) -> str:
    _logger.info('Generating a reset token for %s expiring at %s in %s', account['dn'], expiration, dit.slug)
    random_bytes = os.urandom(_reset_token_random_bytes)
    token_bytes = random_bytes + f'{account["dn"]}{expiration}'.encode('utf-8')
    token = base64.urlsafe_b64encode(hashlib.sha256(token_bytes).digest()[:_reset_token_length]).decode('utf-8')
    biokey = account.get('biokey', {})
    biokey['reset_token'] = token
    biokey['reset_time'] = expiration.isoformat()
    new_desc = _update_biokey_description(account, biokey)
    with ldap_connection(dit) as connection:
        desc_mod = [(ldap.MOD_REPLACE, 'description', [new_desc])]
        connection.modify_s(account['dn'], desc_mod)
    return token


def create_new_account(fn: str, ln: str, telephone: str, email: str, dit: DirectoryInformationTree) -> str:
    _logger.info('Creating new account for «%s» at «%s» in %s', ln, email, dit.slug)
    account_name = generate_account_name(fn, ln, dit)
    create_account(account_name, fn, ln, email, telephone, _edrn_object_classes, dit.slug, dit)
    return account_name


def get_account_by_uid(uid: str, dit: DirectoryInformationTree) -> dict:
    _logger.info('Looking up EDRN account by uid «%s»', uid)
    with ldap_connection(dit) as connection:
        results = connection.search_s(dit.user_base, dit.user_scope, f'(uid={uid})')
        if len(results) == 0: return None
        return _ldap_to_dict(results[0])


def get_accounts_by_email(email: str, dit: DirectoryInformationTree) -> list:
    _logger.info('Looking up EDRN accounts by email «%s»', email)
    accounts = []
    with ldap_connection(dit) as connection:
        results = connection.search_s(dit.user_base, dit.user_scope, f'(mail={email})')
        for i in results:
            accounts.append(_ldap_to_dict(i))
        return accounts


def reset_password_in_dit(dit: DirectoryInformationTree, uid: str, new_password: str):
    '''Set the password for `uid` to `new_password` in the `dit` and clear any reset tokens in the `biokey`.'''
    _logger.info('Resetting password for %s in %s and clearing reset info', uid, dit.slug)
    account = get_account_by_uid(uid, dit)
    if not account:
        raise ValueError(f"uid {uid} doesn't exist in {dit.slug}")
    biokey = account.get('biokey', {})
    for key in ('reset_token', 'reset_time'):
        try:
            del biokey[key]
        except KeyError:
            pass
    description = _update_biokey_description(account, biokey)
    pw = _hash_password(new_password)

    with ldap_connection(dit) as connection:
        modlist = [
            (ldap.MOD_REPLACE, 'description', [description]),
            (ldap.MOD_REPLACE, 'userPassword', [pw])
        ]
        connection.modify_s(account['dn'], modlist)


def verify_password(dit: DirectoryInformationTree, uid: str, password: str) -> bool:
    '''Check if `uid` has valid `password` in the LDAP of `dit`.'''
    dn = f'uid={uid},{dit.user_base}'
    with ldap_connection(dit) as connection:
        try:
            connection.bind_s(dn, password)
            return True
        except ldap.INVALID_CREDENTIALS:
            pass
    return False


def change_password(dit: DirectoryInformationTree, uid: str, password: str):
    '''Change the password in the directory represented by `dit` for `uid` to `password`.'''
    dn = f'uid={uid},{dit.user_base}'
    with ldap_connection(dit) as connection:
        modlist = [(ldap.MOD_REPLACE, 'userPassword', [_hash_password(password)])]
        connection.modify_s(dn, modlist)
