# encoding: utf-8

'''🧬🔑 BioKey site policy.'''

from .celery import app as celery_app
import importlib.resources


PACKAGE_NAME = __name__
__version__ = VERSION = importlib.resources.files(__name__).joinpath('VERSION.txt').read_text().strip()


__all__ = (
    celery_app,
    PACKAGE_NAME,
    VERSION,
)
