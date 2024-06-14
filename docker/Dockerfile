# BioKey — Container Image
# ========================

FROM alpine:3.19


# Configurable Arguments
# ----------------------
#
# - `user_id` defaults to 500 but you can override this if needed.

ARG user_id=500


# Environment Variables
# ---------------------
#
# This doesn't need to be overridden

ENV PYTHONUNBUFFERED=1


# Layers (like Ogres)
# -------------------
#
# Build up the content of the image.
#
#
# Base Packages
# ~~~~~~~~~~~~~

RUN \
    : Add system -S group for biokey, group ID -g &&\
    /usr/sbin/addgroup -S -g $user_id biokey &&\
    : Add system -S user for biokey with no password -D, group biokey -g, user ID -u, gecos info -g, home dir -h &&\
    /usr/sbin/adduser -S -D -h /biokey -G biokey -u $user_id -g 'BioKey user' biokey &&\
    : Separate installations into a separate "virtual" package for easy removal at the end &&\
    build_deps="automake bzip2-dev cyrus-sasl-dev git g++ gcc libffi-dev libjpeg-turbo-dev libwebp-dev libxml2-dev libxslt-dev make musl-dev openjpeg-dev openldap-dev openssl-dev pcre-dev python3-dev postgresql-dev su-exec tiff-dev zlib-dev py3-pip" &&\
    run_deps="curl krb5-libs libgcc libjpeg-turbo libldap libpq libsasl libstdc++ libwebp libxml2 libxslt netcat-openbsd openjpeg python3 rsync tiff tidyhtml" &&\
    /sbin/apk update --quiet &&\
    /sbin/apk add --no-progress --quiet --virtual build $build_deps &&\
    /sbin/apk add --no-progress --quiet $run_deps &&\
    : See https://github.com/python-ldap/python-ldap/issues/432 for workaround to Python LDAP vs OpenLDAP 2.5 issue &&\
    echo 'INPUT ( libldap.so )' > /usr/lib/libldap_r.so &&\
    :


# Spot Check
# ~~~~~~~~~~
#
# Over on GitHub Actions, we need to fail fast and not hit the six hour run limit, so make sure we got it right

RUN [ `/usr/bin/python3 --version | sed -E 's/[^0-9]*([0-9]+\.[0-9]+)\.[0-9]+/\1/'` = "3.11" ]


# Application Specifics and Clean Up
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# This is handy for development:

RUN :&&\
    echo 'TLS_REQCERT never' >> /etc/openldap/ldap.conf &&\
    :

# The real app setup follows:

RUN : &&\
    /usr/bin/python3 -m venv /app &&\
    /usr/bin/install -o biokey -g biokey -d /app/media /app/static /app/wheels &&\
    /app/bin/python3 -m ensurepip --upgrade &&\
    /app/bin/pip3 install --quiet --progress-bar off --upgrade pip setuptools wheel &&\
    /app/bin/pip3 install gunicorn==20.1.0 &&\
    :

COPY --chown=biokey:biokey ./dist/*.whl /app/wheels/
RUN /app/bin/pip3 install --progress-bar off /app/wheels/*.whl

RUN :&&\
    cd /app &&\
    : Get the static files ready &&\
    /sbin/su-exec biokey /usr/bin/env LDAP_BIND_PASSWORD=unused SIGNING_KEY=unused /app/bin/django-admin collectstatic --settings jpl.edrn.biokey.policy.settings.ops --no-input --clear --link &&\
    :

RUN :&&\
    : Get database migrations ready and no I have no idea why we have to do wagtailcore first &&\
    /usr/bin/env LDAP_BIND_PASSWORD=unused SIGNING_KEY=unused /app/bin/django-admin makemigrations --settings jpl.edrn.biokey.policy.settings.ops --no-input --scriptable wagtailcore &&\
    :

RUN :&&\
    : Get database migrations ready and no I have no idea why we have to do wagtail_favicon first &&\
    /usr/bin/env LDAP_BIND_PASSWORD=unused SIGNING_KEY=unused /app/bin/django-admin makemigrations --settings jpl.edrn.biokey.policy.settings.ops --no-input --scriptable wagtail_favicon &&\
    :

RUN :&&\
    : Get database migrations ready and no I have no idea why we have to do robots first &&\
    /usr/bin/env LDAP_BIND_PASSWORD=unused SIGNING_KEY=unused /app/bin/django-admin makemigrations --settings jpl.edrn.biokey.policy.settings.ops --no-input --scriptable robots &&\
    :

RUN :&&\
    : =================== wtf ==================== &&\
    /usr/bin/env LDAP_BIND_PASSWORD=unused SIGNING_KEY=unused /app/bin/django-admin makemigrations --settings jpl.edrn.biokey.policy.settings.ops --no-input --scriptable &&\
    :

RUN \
    : Clean up clean up everybody everywhere &&\
    : PrismaCloud does not like pip to be in the image &&\
    /app/bin/pip3 uninstall --yes --quiet pip &&\
    /sbin/apk del --quiet build &&\
    /bin/rm -rf /app/wheels &&\
    /bin/rm -rf /var/cache/apk/* &&\
    /bin/chown -R biokey:biokey /app/lib/python3.*/site-packages &&\
    :

COPY --chown=biokey:biokey docker/*.py /app/


# Image Morphology
# ----------------

# Define external shape and other miscellaneous details of the image.

EXPOSE      8000
VOLUME      ["/app/media"]
USER        biokey
WORKDIR     /app
ENTRYPOINT  ["/app/bin/gunicorn"]
HEALTHCHECK --interval=5m --timeout=2m --start-period=10m CMD /usr/bin/curl --fail --retry 6 --max-time 5 --retry-delay 10 --retry-max-time 60 http://127.0.0.1:8000/ || /bin/sh -c 'killall5 -TERM && (/bin/sleep 10; killall5 -KILL)'


# Metadata
# --------
#
# Note that ``org.label-schema`` is deprecated, but it's a heck of a lot easier to understand. Still, why not just
# use the Dublin Core?

LABEL "org.label-schema.name"="BioKey"
LABEL "org.label-schema.version"="0.0.0"
