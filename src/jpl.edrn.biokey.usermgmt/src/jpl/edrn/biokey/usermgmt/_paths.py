# encoding: utf-8

'''🧬🔑🕴️ BioKey user management: path handling.'''


from django.conf import settings
from django.http import HttpRequest
from wagtail.models import Site


def make_pwreset_url(slug: str, uid: str, token: str, request: HttpRequest) -> str:
    '''Create a password reset URL suitable for the pattern in `urls.py`.'''

    current_site = Site.find_for_request(request)
    if not current_site:
        current_site = Site.objects.get(is_default_site=True)

    scheme = 'https' if request.is_secure() else 'http'
    base_url = f'{scheme}://{current_site.hostname}'
    if current_site.port and current_site.port not in (80, 443):
        base_url += f':{current_site.port}'
    if settings.FORCE_SCRIPT_NAME:
        base_url += settings.FORCE_SCRIPT_NAME

    return f'{base_url}/pwreset/{slug}/{uid}/{token}'


# In retrospect, this shouldn't be a view, but a child page of the
# DirectoryInformationTree, so coming up with URLs like the above
# wouldn't be necessary.
