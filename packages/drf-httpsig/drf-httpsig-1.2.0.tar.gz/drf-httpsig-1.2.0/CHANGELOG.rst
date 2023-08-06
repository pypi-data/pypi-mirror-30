drf-httpsig Changes
===================

v1.2.0 (2018-Mar-28)
--------------------

* Updated to support and require httpsig 1.x.
* Switched to pytest over nose

v1.1.0 (2015-Feb-11)
--------------------

* Updated to support and require httpsig 1.1.
* Updated requirements to simply Django<1.7 and DRF<3.0. Last version for those, I suspect.

v1.0.2 (2014-Jul-24)
--------------------

* Updated authentication return value to set request.auth to the key_id used.

v1.0.1 (2014-Jul-03)
--------------------

* Added/verified Python 3 support and tests (3.2+).
* Added support for sending a DRF authorization challenge if we're the primary authenticator.
* Switched to using the `httpsig` HeaderVerifier instead of doing it ourselves. Lots of code got deleted there.
* Changed fetch_user_data to also receive the algorithm the keyID is for.
* Updated README.
* Removed models.py -- the client should handle that part entirely.

v1.0b2/1.0.0 (2014-Jul-01)
--------------------------

* Added versioneer.
* Updated requirements to use latest httpsig.
* Added "setup.py test" and tox support.
* Fixed a unit test.

v1.0b1 (2014-Jun-27)
--------------------

* Renamed to drf-httpsig because I don't hate my hands.
* Updated requirements versions to be more sane.
* Switched to a different branch for http_signature.
* Removed API_KEY_HEADER in favor of the keyId, per spec.
* Cleaned up the repo a bit.
* Cleaned up the code a bit.


djangorestframework-httpsignature (previous)
============================================

v0.1.5, 20140613 -- Document installation issue

* Document workaround on installation problems.

v0.1.4, 20140613 -- Improve installation

* Make requirements file comply with docs.
* Decide on http_signature commit.

v0.1.3, 20140220 -- Upload to PyPI

* Prepare docs to upload package to PyPI

v0.1.2, 20140219 -- Package data and clean up

* Updated package classifiers
* Cleaned up unused code in authentication.py

v0.1.1, 20140217 -- Documentation and clean up

* The package can be installed.
* Continuous integration via Travis.
* Unit tests for the authentication code.
* General docuementation in the README file.

v0.1.0, 20140217 -- Initial release
