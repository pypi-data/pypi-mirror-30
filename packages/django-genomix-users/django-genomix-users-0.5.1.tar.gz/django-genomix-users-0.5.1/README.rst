=============================
Django GenomiX Users
=============================

.. image:: https://badge.fury.io/py/django-genomix-users.svg
    :target: https://badge.fury.io/py/django-genomix-users

.. image:: https://travis-ci.org/chopdgd/django-genomix-users.svg?branch=develop
    :target: https://travis-ci.org/chopdgd/django-genomix-users

.. image:: https://codecov.io/gh/chopdgd/django-genomix-users/branch/develop/graph/badge.svg
    :target: https://codecov.io/gh/chopdgd/django-genomix-users

.. image:: https://pyup.io/repos/github/chopdgd/django-genomix-users/shield.svg
     :target: https://pyup.io/repos/github/chopdgd/django-genomix-users/
     :alt: Updates

.. image:: https://pyup.io/repos/github/chopdgd/django-genomix-users/python-3-shield.svg
      :target: https://pyup.io/repos/github/chopdgd/django-genomix-users/
      :alt: Python 3

Core library for Nexus django applications that require User accounts

Documentation
-------------

The full documentation is at https://django-genomix-users.readthedocs.io.

Quickstart
----------

Install Django GenomiX Users::

    pip install django-genomix-users

Make the following changes to `INSTALLED_APPS` in `settings.py` file:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.staticfiles',
        ...
        'rest_framework',
        'rest_framework.authtoken',
        'rest_auth',
        'django_filters',
        ...
        'django_python3_ldap',
        ...
        'genomix_users',
        ...
    )

Add Django GenomiX Users's URL patterns:

.. code-block:: python

    from genomix_users import urls as genomix_users_urls


    urlpatterns = [
        ...
        url(r'^', include(genomix_users_urls, namespace='users')),
        ...
    ]

Make sure `settings.py` file has `TEMPLATES` and `STATIC_URL` set (example below):

.. code-block:: python

    TEMPLATES = [
        {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
            'DIRS': [
                os.path.join(ROOT_DIR, 'templates'),
                os.path.join(APPS_DIR, 'templates'),
            ],
            'OPTIONS': {
                # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
                'debug': DEBUG,
                # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
                # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
                'loaders': [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ],
                # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.template.context_processors.i18n',
                    'django.template.context_processors.media',
                    'django.template.context_processors.static',
                    'django.template.context_processors.tz',
                    'django.contrib.messages.context_processors.messages',
                    # Your stuff: custom template context processors go here
                ],
            },
        },
    ]

    STATIC_URL = '/static/'

Make sure `settings.py` file has `MIDDLEWARE` set (example below):

.. code-block:: python

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

Optional settings
-----------------

Turn off the creation of associated user profiles in `settings.py`.

.. code-block:: python

    CREATE_PROFILE_ON_SAVE = False

Enable authentication to use JSON Web Token in `settings.py`:

.. code-block:: python

    REST_USE_JWT = True

    REST_FRAMEWORK = {
        'DEFAULT_PERMISSION_CLASSES': (
            'rest_framework.permissions.IsAuthenticated',
        ),
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
            'rest_framework.authentication.SessionAuthentication',
            'rest_framework.authentication.BasicAuthentication',
        ),
    }

Enable LDAP authentication in `settings.py`:

.. code-block:: python

    LDAP_AUTH_URL = 'ldap://chop.edu:3268'

    LDAP_AUTH_USE_TLS = False

    LDAP_AUTH_SEARCH_BASE = 'dc=chop,dc=edu'

    LDAP_AUTH_OBJECT_CLASS = 'person'

    LDAP_AUTH_USER_LOOKUP_FIELDS = ('username',)

    LDAP_AUTH_USER_FIELDS = {
        "username": "sAMAccountName",
        "first_name": "givenName",
        "last_name": "sn",
        "email": "mail",
    }

    LDAP_AUTH_FORMAT_USERNAME = 'django_python3_ldap.utils.format_username_active_directory'

    LDAP_AUTH_ACTIVE_DIRECTORY_DOMAIN = 'chop-edu'

    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
        'django_python3_ldap.auth.LDAPBackend',
    ]

Enable LDAP User group filtering in `settings.py`:

.. code-block:: python

    LDAP_AUTH_FORMAT_SEARCH_FILTERS = 'genomix_users.authentication.genomix_search_filters'

    LDAP_AUTH_SEARCH_FILTER = 'CN=dgd_nexus_users,ou=DGD Groups,ou=SecurityGroups,ou=Research,ou=Managed By Others,dc=chop,dc=edu'

Sync User Profile with LDAP fields in `settings.py`:

.. note:: If `CREATE_PROFILE_ON_SAVE = False`, LDAP profile will not sync!

.. code-block:: python

    LDAP_AUTH_SYNC_USER_RELATIONS = "genomix_users.authentication.sync_genomix_profile"

    # User model fields mapped to the LDAP attributes that represent them.
    LDAP_AUTH_PROFILE_FIELDS = {
        "title": "title",
    }

Features
--------

* GenomiX REST API for authentication using `django-rest-auth <https://github.com/Tivix/django-rest-auth>`_
* GenomiX LDAP authentication using `django-python3-ldap <https://github.com/etianen/django-python3-ldap>`_

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
