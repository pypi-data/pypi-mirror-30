=============================
telegram_bots
=============================

.. image:: https://badge.fury.io/py/telegram_bots.svg
    :target: https://badge.fury.io/py/telegram_bots

.. image:: https://travis-ci.org/narnikgamarnikus/telegram_bots.svg?branch=master
    :target: https://travis-ci.org/narnikgamarnikus/telegram_bots

.. image:: https://codecov.io/gh/narnikgamarnikus/telegram_bots/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/narnikgamarnikus/telegram_bots

App for creating telegram bots, with setting webhook, receive messages and subscribe users

Documentation
-------------

The full documentation is at https://telegram_bots.readthedocs.io.

Quickstart
----------

Install telegram_bots::

    pip install telegram_bots

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'telegram_bots.apps.TelegramBotsConfig',
        ...
    )

Add telegram_bots's URL patterns:

.. code-block:: python

    from telegram_bots import urls as telegram_bots_urls


    urlpatterns = [
        ...
        url(r'^', include(telegram_bots_urls)),
        ...
    ]

Features
--------

* TODO

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
