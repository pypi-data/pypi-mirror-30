===================
djangocms-page-tags
===================

.. image:: https://img.shields.io/pypi/v/djangocms-page-tags.svg
        :target: https://pypi.python.org/pypi/djangocms-page-tags
        :alt: Latest PyPI version

.. image:: https://img.shields.io/travis/nephila/djangocms-page-tags.svg
        :target: https://travis-ci.org/nephila/djangocms-page-tags
        :alt: Latest Travis CI build status

.. image:: https://coveralls.io/repos/nephila/djangocms-page-tags/badge.png
        :target: https://coveralls.io/r/nephila/djangocms-page-tags
        :alt: Test coverage

Tagged pages for django CMS 3

Python: 2.7, 3.4, 3.5, 3.6

Django: 1.8 to 1.11

django CMS: 3.4 (and develop/3.5)

.. warning:: Since version 0.5, the support for Python 2.6, Python 3.3, Django<1.8 and django CMS<3.2
             has been dropped

**********
Quickstart
**********

Install djangocms-page-tags::

    pip install djangocms-page-tags

Then add it to INSTALLED_APPS along with its dependencies::

    'taggit',
    'taggit_autosuggest',
    'djangocms_page_tags',

Add `taggit_autosuggest` to urlconf::

    url(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),


Execute migration or syncdb::

    $ python manage.py syncdb

or::

    $ python manage.py migrate

*****
Usage
*****

You will find two new items in the toolbar Page menu:

* Title tags (per language)
* Page tags (global)

These items allows to add tags to ``Title`` and ``Page`` instances, respectively

************
Templatetags
************

``djangocms-page-tags`` allows showing tags using four templatetags

* ``include_page_tags``
* ``include_title_tags``
* ``page_tags``
* ``title_tags``

*************
Documentation
*************

For further documentation see https://djangocms-page-tags.readthedocs.io/




*******
History
*******

0.6.1 (2018-03-29)
==================

* Properly set migration dependencies
* Improve compatibility with django CMS 3.5
* Fix issues with tox on travis

0.6.0 (2017-12-30)
==================

* Add Django 1.11 support
* Drop django CMS 3.2, 3.3

0.5.0 (2016-12-02)
==================

* Add Django 1.10 support
* Add support for django CMS 3.3, 3.4
* Drop Django 1.7 and below
* Drop django CMS 3.1 and below

0.4.2 (2016-01-08)
==================

* Fix handling of pages in non existing languages

0.4.1 (2015-10-03)
==================

* Add support for django CMS 3.2
* Add support for Django 1.8
* Update translation
* PEP-8 / isort code cleanup

0.4.0 (2015-06-29)
==================

* Add support for django CMS 3.1
* Add support for Django 1.7
* Use djangocms-helper for testing

0.3.0 (2014-04-20)
==================

* Support for django CMS 3.0 final

0.2.1 (2014-03-29)
==================

* Support for django CMS 3.0 RC1
* Add verbose description

0.2.0 (2014-02-02)
==================

* Fix for django CMS 3 develop update

0.1.4 (2014-01-26)
==================

* Metadata cleanup

0.1.3 (2014-01-22)
==================

* Put toolbar menu items in a submenu

0.1.2 (2014-01-16)
==================

* Documentation update

0.1.1 (2014-01-16)
==================

* Add transifex support

0.1.0 (2014-01-15)
==================

* Experimental release.


