# encoding: utf-8

'''🧬🔑🕴️ BioKey user management.'''

import importlib.resources


PACKAGE_NAME = __name__
__version__ = VERSION = importlib.resources.files(__name__).joinpath('VERSION.txt').read_text().strip()


__all__ = (
    PACKAGE_NAME,
    VERSION,
)
