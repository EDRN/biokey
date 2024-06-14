#!/bin/sh -e
#
# Run django-admin locally with this convenience script

. ${HOME}/.secrets/passwords.sh

export DJANGO_SETTINGS_MODULE=local

if [ ! -d "src" -o ! -d "etc" -o ! -d "docker" ]; then
    echo "🚨 Run this from the checked-out BioKey source directory" 1>&2
    echo "You should have these subdirs in the current directory: src etc docker" 1>&2
    exit 1
fi

if [ -d ".venv/lib/python3.11/site-packages/jpl" ]; then
    echo "⚠️ Somehow in-development eggs got expanded in the site-packages dir!" 1>&2
    echo "Nuking the .venv so we're forced to start over" 1>&2
    rm -rf ".venv"
fi

if [ ! -d ".venv" ]; then
    echo "⚠️ Local Python virtual environment missing; attempting to re-create it" 1>&2
    python3.11 -m venv .venv
    .venv/bin/pip install --quiet --upgrade setuptools pip wheel build
    .venv/bin/pip install --editable src/jpl.edrn.biokey.theme[dev]
    .venv/bin/pip install --editable src/jpl.edrn.biokey.streams[dev]
    .venv/bin/pip install --editable src/jpl.edrn.biokey.content[dev]
    .venv/bin/pip install --editable src/jpl.edrn.biokey.usermgmt[dev]
    .venv/bin/pip install --editable src/jpl.edrn.biokey.policy[dev]
fi

command="$1"
shift
exec /usr/bin/env \
    LDAP_URI="ldaps://localhost:1637" \
    DATABASE_URL="postgresql://:@/biokey" \
    ".venv/bin/django-admin" $command --settings local --pythonpath . "$@"
