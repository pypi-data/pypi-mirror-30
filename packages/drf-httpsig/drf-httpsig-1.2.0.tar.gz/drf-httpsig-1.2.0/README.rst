drf-httpsig
===========

Easy `HTTP Signature`_ authentication support for the `Django REST framework`_.


Overview
--------

The HTTP Signature scheme provides a way to achieve origin authentication and message integrity for HTTP messages. Similar to Amazon's `HTTP Signature scheme`_, used by many of its services. The `HTTP Signature`_ specification is currently an IETF draft.


.. contents::

Requirements
------------

* Python 2.7, 3.3+ (currently tested up to 3.4)
* `httpsig`_


Installation
------------

This module uses `setuptools` and is hosted on PyPi so installation is as easy as::

   pip install drf-httpsig

This should also install the `httpsig`_ module which houses all the magic; this module is pure DRF glue (as it should be).

You can also run `setup.py` from inside a clone of the repository::

    python setup.py install

Note that if you do so, modules with a version requirement may attempt to re-install the module as `versioneer` may report a different version, especially if your clone of the repo has any uncommitted/untagged changes.


Running the Tests
-----------------

To run the tests for the module, use the following command on the repository root directory::

  python setup.py test

Note that testing depends on `django-nose`, which will be installed before testing. You may also run the tests with `tox` using the included `tox.ini` file which has the benefit of keeping all testing dependances in a venv automatically.:

    tox -e py27,py32,...


Usage
-----

To actually authenticate HTTP requests with this module, you need to extend the ``SignatureAuthentication`` class, as follows:

.. code:: python

    # my_api/auth.py

    from drf_httpsig.authentication import SignatureAuthentication

    class MyAPISignatureAuthentication(SignatureAuthentication):
        # The HTTP header used to pass the consumer key ID.

        # A method to fetch (User instance, user_secret_string) from the
        # consumer key ID, or None in case it is not found. Algorithm
        # will be what the client has sent, in the case that both RSA
        # and HMAC are supported at your site (and also for expansion).
        def fetch_user_data(self, key_id, algorithm="hmac-sha256"):
            # ...
            # example implementation:
            try:
                user = User.objects.get(keyId=key_id, algo=algorithm)
                return (user, user.secret)
            except User.DoesNotExist:
                return (None, None)


4. Configure DRF to use your authentication class; e.g.:

.. code:: python

    # my_project/settings.py

    # ...
    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
           'my_api.auth.MyAPISignatureAuthentication',
        ),
        'DEFAULT_PERMISSION_CLASSES': (
            'rest_framework.permissions.IsAuthenticated',
        )
    }
    # The above will force HTTP signature for all requests.
    # ...


Support
-------

Please file any issues in the `issue tracker`_.  You are also welcome to contribute features and fixes via pull requests.


Example Usage and Session w/cURL
--------------------------------

Assuming the setup detailed above, a project running on ``localhost:8000`` could be probed with cURL as follows::

    # Pre-calculate this first bit.
    ~$ SSS=Base64(Hmac(SECRET, "Date: Mon, 17 Feb 2014 06:11:05 GMT", SHA256))
    ~$ curl -v -H 'Date: "Mon, 17 Feb 2014 06:11:05 GMT"' -H 'Authorization: Signature keyId="my-key",algorithm="hmac-sha256",headers="date",signature="SSS"'

And, with much less pain, using the modules ``requests`` and ``httpsig``:

.. code:: python

    import requests
    from httpsig.requests_auth import HTTPSignatureAuth

    KEY_ID = 'su-key'
    SECRET = 'my secret string'

    signature_headers = ['(request-target)', 'accept', 'date', 'host']
    headers = {
      'Host': 'localhost:8000',
      'Accept': 'application/json',
      'Date': "Mon, 17 Feb 2014 06:11:05 GMT"
    }

    auth = HTTPSignatureAuth(key_id=KEY_ID, secret=SECRET,
                           algorithm='hmac-sha256',
                           headers=signature_headers)
    req = requests.get('http://localhost:8000/resource/',
                     auth=auth, headers=headers)
    print(req.content)


.. References:

.. _`HTTP Signature`: https://datatracker.ietf.org/doc/draft-cavage-http-signatures/
.. _`Django REST framework`: http://django-rest-framework.org/
.. _`HTTP Signature scheme`: http://docs.aws.amazon.com/general/latest/gr/signature-version-4.html
.. _`httpsig`: https://github.com/ahknight/httpsig
.. _`issue tracker`: https://github.com/ahknight/httpsig/issues
