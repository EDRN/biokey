#!/bin/sh -e
#
# Rebuild for developement

# Secrets

. ${HOME}/.secrets/passwords.sh
DEFAULT_LDAP_SERVER_PASSWORD=$edrn_ldap_manager_password
export DEFAULT_LDAP_SERVER_PASSWORD

# Argument check

if [ $# -ne 0 ]; then
    echo "😩 This program takes no arguments; try again?" 1>&2
    exit 1
fi


# Sentinel files check

if [ ! -f "manage.sh" -o ! -f "local.py" ]; then
    echo "🚨 Run this from the checked out biokey repository; you should have" 1>&2
    echo "manage.sh and local.py files in the current directory. You may have to" 1>&2
    echo "create local.py, setting SECRET_KEY to anything and ALLOWED_HOSTS to a list of"
    echo "just the single character *. You can also disable CACHES and turn off the" 1>&2
    echo "SILENCED_SYSTEM_CHECKS for captcha.recaptcha_test_key_error while in" 1>&2
    echo "development." 1>&2
    exit 1
fi


# Normally we'd need to transfer an existing database, but we're starting off from scratch
# here.
#
# jpl_sys_ipv4=172.16.16.3

# Warning

cat <<EOF
❗️ This program will wipe out your local "biokey" PostgreSQL database.

If you have any local changes to your content database or media blobs
you want to preserve, abort now!

⏱️ You have 5 seconds.
EOF


# Here we go

sleep 5
trap 'echo "😲 Interrupted" 1>&2; exit 1' SIGINT

echo "🏃‍♀️Here we go"
dropdb --force --if-exists "biokey"
createdb "biokey" 'Database for BioKey'

# Normally we'd need to transfer an existing database, but we're starting off from scratch
# here.
#
# Must use --checksum here because the nightly refresh from NCI to tumor munges all the timestamps
# rsync --checksum --no-motd --recursive --delete --progress $jpl_sys_ipv4:/Users/kelly/biokey/media .
# scp $jpl_sys_ipv4:/Users/kelly/biokey/biokey.sql.bz2 .
# bzip2 --decompress --stdout biokey.sql.bz2 | psql --dbname=biokey --echo-errors --quiet

./manage.sh makemigrations
./manage.sh migrate
./manage.sh collectstatic --no-input --clear --link


# Add additional upgrade steps here:

./manage.sh biokey_bloom --hostname localhost --port 6468 --ldap-uri ldaps://localhost:1636

# And make development a breeze

./manage.sh clear_cache --all

echo '🏁 Done! You can start it with:'
echo './manage.sh runserver 6468'

exit 0
