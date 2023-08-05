

===========
wagtail-2fa
===========

This Django app add's two factor authentication to Wagtail. Behind the scenes
it use django-otp_ which supports Time-based One-Time Passwords (TOTP). This
allows you to use various apps like Authy, Google Authenticator, or
1Password.


.. _django-otp: https://django-otp-official.readthedocs.io


Installation
============

.. code-block:: shell

   pip install wagtail-2fa


Then add the following lines before the wagtail apps in to the
``INSTALLED_APPS`` list in your Django settings:

.. code-block:: python

    INSTALLED_APPS = [
        'wagtail_2fa',
        'django_otp',
        'django_otp.plugins.otp_totp',

        # other apps
    ]


Next add the required middleware to the ``MIDDLEWARE``. It should come
after the AuthenticationMiddleware:

.. code-block:: python

    MIDDLEWARE = [
        # .. other middleware
        # 'django.contrib.auth.middleware.AuthenticationMiddleware',

        'wagtail_2fa.middleware.VerifyUserMiddleware',

        # 'wagtail.core.middleware.SiteMiddleware',
        # .. other middleware
    ]


Settings
========

The following settings are available (Set via your Django settings):

    - ``WAGTAIL_2FA_REQUIRED`` (default ``False``): When set to True all
      staff, superuser and other users with access to the Wagtail Admin site
      are forced to login using two factor authentication.




