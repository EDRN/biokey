# 🧬🔑 BioKey

BioKey is the cancer bioinformatics user registration and profile application.

It's to enable current and future users of [LabCAS](https://edrn-labcas.jpl.nasa.gov/) to help manage their identities, including:

- Registering for a non-[EDRN](https://edrn.nci.nih.gov/) account
- Updating your details, such as your email address or name
- Changing your non-EDRN password

👉 **Note:** If you have an account with EDRN (Early Detection Research Network), you can use it to access LabCAS and other EDRN applications. If you're not sure if you have an account, visit the [EDRN Data Management and Coordinating Center](https://www.compass.fhcrc.org/enterEDRN/) and try to log in. If you can't, you don't.


## 🤓 Development

Make the DB

    createdb biokey
    ./manage.sh makemigrations
    ./manage.sh migrate wagtailimages  # not sure why this needs to be done separately
    ./manage.sh migrate

Maybe this is needed?

    ./manage.sh makemigrations --empty jpledrnbiokeystreams
    ./manage.sh makemigrations --empty jpledrnbiokeypolicy
    ./manage.sh makemigrations jpledrnbiokeycontent
    ./manage.sh makemigrations

Launch it

    ./manage.sh runserver 6468  # or pick your favorite port


### Essential Environment Variables

TBD.


### Database

TBD.


### Software Installation

TBD.


## 🚢 Containerized Setup

TBD.

### 🎑 Image Building

First, build the wheels by running:

    support/build-wheels.sh

Then build the image:

    docker image build --file docker/Dockerfile --tag edrndocker/biokey .

You can do a spot check to see if the image is viable by running

    docker container run --rm --env SIGNING_KEY=key --env ALLOWED_HOSTS='*' --publish 8000:8000 \
        edrndocker/biokey:latest

and then visiting http://localhost:8000/. If you get "Server Error (500)", congratulations! It's working.

To launch the orchestrated services (BioKey application, PostgreSQL database, Redis cache/message queue, and Celery worker)—or in other words, to _start the composition_—run:

    docker compose --project-name biokey --file docker/docker-compose.yaml up --detach

Note the many environment variables that are needed. You'll want to put these into a `.env` file; see the "Environemnt Variables" section, below. Also, after the first launch only, the database is empty and needs to be structured and populated; see the next section.


### 📀 Containerized Database Setup

Create the `biokey` database in PostgreSQL:

    docker compose --project-name biokey --file docker/docker-compose.yaml \
        exec db createdb --username=postgres --encoding=UTF8 --owner=postgres biokey

Make sure the `POSTGRES_PASSWORD` environment variable has the same value when running this command as you did when you started the composition, above.

Next, run the Django database migrations to turn the empty `biokey` database into a Django-, Wagtail-, and BioKey-capable database:

    docker compose --project-name biokey --file docker/docker-compose.yaml \
        exec app /app/bin/django-admin migrate

Finally, populate the content with:

    docker compose --project-name biokey --file docker/docker-compose.yaml \
        exec app /app/bin/django-admin biokey_bloom



### 🪶 Front End Web Server

TBD.



#### 🏛 Database Structure

TBD.


#### 🥤 Initial Form and Content Population

TBD.


#### 🔻 Subpath Serving

TBD.


### 🍃 Container Environment Variables

TBD.


### 🍃 Environment Variable Reference

| Variable                         | Purpose                                                   | Default |
|:---------------------------------|:----------------------------------------------------------|:--------|
| `ALLOWED_HOSTS`                  | Valid `Host` HTTP headers; others rejected                | `.jpl.nasa.gov` |
| `BASE_URL`                       | Base URL for Wagtail admin interface for generated emails | `https://edrn-labcas.jpl.nasa.gov/biokey/` |
| `BIOKEY_VERSION`                 | Version of the BioKey image in Docker Composition         | `latest` |
| `CACHE_URL`                      | URL to the cache service                                  | `redis://` |
| `CERT_CN`                        | Common name of random TLS certificate                     | `edrn-docker.jpl.nasa.gov` |
| `CSRF_TRUSTED_ORIGINS`           | Comma-separated URLs that provide trusted resources       | `http://*.jpl.nasa.gov,https://*.jpl.nasa.gov` |
| `DATA_DIR`                       | Where Docker Composition can persist voumes               | `/usr/local/labcas/biokey/ops/dockerdata` |
| `EMAIL_HOST_PASSWORD`            | Password to log into SMTP server                          | (unset) |
| `EMAIL_HOST_USER`                | Username to log into SMTP server                          | (unset) |
| `EMAIL_HOST`                     | Host name of SMTP server                                  | `smtp.jpl.nasa.gov` |
| `EMAIL_PORT`                     | Port number of SMTP server                                | `587` |
| `EMAIL_USE_SSL`                  | `True` if to use SSL to access SMTP server                | `False` |
| `EMAIL_USE_TLS`                  | `True` if to use TLS to access SMTP server                | `True` |
| `FORCE_SCRIPT_NAME`              | Subpath if the app isn't at the root URL                  | (unset, except `/biokey/` in Docker Composition) |
| `HTTP_PORT`                      | `http` non-TLS port for BioKey (see `PROXY_PORT` for TLS) | 8080 |
| `IMAGE_RENDITIONS_CACHE_SIZE`    | How many various resolutions of images to cache           | 1000 |
| `IMAGE_RENDITIONS_CACHE_TIMEOUT` | How long to cache image renditions (seconds)              | 86400 |
| `LDAP_CACHE_TIMEOUT`             | Timeout in seconds to cache results from `LDAP_URI`       | 3600 |
| `LDAP_URI`                       | LDAP server for Wagtail administrator authentication      | `ldaps://ldap-202007.jpl.nasa.gov` |
| `MEDIA_ROOT`                     | Filesystem location of user media                         | `$CWD/media` |
| `MEDIA_URL`                      | URL to user media (images, documents)                     | `/media/` |
| `MQ_URL`                         | URL to message queue                                      | `redis://` |
| `POSTGRES_PASSWORD`              | Root password to Postgres DB in Docker Composition        | (unset) |
| `PROXY_PATH`                     | Subpath in TLS-termination of BioKey                      | `/biokey/` in Docker Composition |
| `HTTPS_PORT`                     | Host port to bind to for TLS-based termination of BioKey  | `4234` |
| `RECAPTCHA_PRIVATE_KEY`          | Private key of reCAPTCHA service                          | (unset) |
| `RECAPTCHA_PUBLIC_KEY`           | Public key of reCAPTCHA service                           | (unset) |
| `SECURE_COOKIES`                 | `True` if to use secure (HTTPS) cookies only              | `True` |
| `SIGNING_KEY`                    | Opaque key used to sign secrets                           | (unset but required)
| `STATIC_ROOT`                    | Filesystem location of static files                       | `$CWD/static` |
| `STATIC_URL`                     | URL to static resources                                   | `/static/` |

## 👩‍💻 Software Environment

TBD.


### 👥 Contributing

You can start by looking at the [open issues](https://github.com/EDRN/biokey/issues), forking the project, and submitting a pull request. You can also [contact us by email](mailto:ic-portal@jpl.nasa.gov) with suggestions.


### 🔢 Versioning

We use the [SemVer](https://semver.org/) philosophy for versioning this software. For versions available, see the [releases made](https://github.com/EDRN/biokey/releases) on this project.


## 👩‍🎨 Creators

The principal developer is:

- [Sean Kelly](https://github.com/nutjob4life)

The QA team consists of:

- [Heather Kincaid](https://github.com/hoodriverheather)

To contact the team as a whole, [email the Informatics Center](mailto:ic-portal@jpl.nasa.gov).


## 📃 License

The project is licensed under the [Apache version 2](LICENSE.md) license.
