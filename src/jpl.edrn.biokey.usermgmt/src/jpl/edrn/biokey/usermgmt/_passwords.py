# encoding: utf-8

'''🧬🔑🕴️ BioKey user management: password handling.'''


import re, random, string

_random_password_corpus = string.ascii_letters + string.digits
_random_password_length = 20


def check_complexity(password: str) -> bool:
    '''Check if the `password` is complex enough and return True if it is.

    We allow and encourage pass phrases, so passwords 20 characters or longer are
    considered complex enough. Shorter passwords must have an uppercase character,
    a lowercase character, a digit, and a special symbol.
    '''
    if len(password) >= 20:
        return True
    return True if re.search(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W).+$', password) else False


def generate_random_password() -> str:
    '''Make a random password.

    The password will be `_random_password_length` long and consist of characters from
    the `_random_password_corpus`.
    '''
    return ''.join(random.sample(_random_password_corpus, _random_password_length))
