pdfebc-web - Web interface for the pdfebc tools
***********************************************

`Docs`_

.. image:: https://travis-ci.org/slarse/pdfebc-web.svg?branch=master
    :target: https://travis-ci.org/slarse/pdfebc-web
    :alt: Build Status
.. image:: https://codecov.io/gh/slarse/pdfebc-web/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/slarse/pdfebc-web
    :alt: Code Coverage
.. image:: https://readthedocs.org/projects/pdfebc-web/badge/?version=latest
    :target: http://pdfebc-web.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://badge.fury.io/py/pdfebc-web.svg
    :target: https://badge.fury.io/py/pdfebc-web
    :alt: PyPi Version
.. image:: https://img.shields.io/badge/python-3.6-blue.svg
    :target: https://badge.fury.io/py/pdfebc
    :alt: Supported Python Versions

.. contents::

Overview
========
``pdfebc-web`` is the web based part of the set of `pdfebc-core`_ interfaces. The app is primarily
built with ``Flask``, but ``Celery`` handles CPU-intensive background tasks, such as compressing pdf files.
This is mostly a toy project for me to learn Flask, but someone, somewhere may find it
useful someday. Currently, the features include uploading pdf files, compressing them, and
having them sent to a pre-configured e-mail address.

Requirements
============
Aside from the Python modules listed in `requirements.txt`_, the following requirements must be
met:

* ``Python 3.6``
    - Strictly speaking, 3.5 should also work fine, but the tests use 3.6 features so the
      build is only tested for 3.6.
* ``Ghostscript``
    - ``pdfebc-core`` requires ``Ghostscript`` for the PDF compression. The default binary is ``gs``,
      but this can be specified in the configuration file.
* ``Redis``
    - Celery requires a message broker, and I chose to go with ``Redis``.
* A Gmail account (for sending e-mails)
    - By default, ``pdfebc`` uses Google's SMTP server to send e-mails. The program can however
      be configured to use any SMTP server by maniupulating the ``config.cnf``.

Install
=======
Option 1: Install from PyPi with ``pip``
----------------------------------------
The latest release of ``pdfebc-web`` is on PyPi, and can thus be installed as usual with ``pip``.
I strongly discourage system-wide ``pip`` installs (i.e. ``sudo pip install <package>``), as this
may land you with incompatible packages in a very short amount of time. A per-user install
can be done like this:

1. Execute ``pip install --user pdfebc-web`` to install the package.
2. Install ``Redis`` (used by ``Celery``).
    - This may or may not be available in your package manager, Google it for specifics!
3. Install ``Ghostscript``.
    - Many distributions come with ``Ghostscript`` pre-installed, but you may need to install
      it.
    - Make note of what the binary is called, and enter it in the configuration file
      (see the next step).
4. Currently, you must add the configuration file manually. Please have a look at the
   `sample configuration`_ file for details. Where to put the configuration file is
   machine-dependent, and decided by the ``appdirs`` package.
   On most modern Linux distributions, the file should be put at ``$HOME/.config/pdfebc/config.cnf``.
   You can run ``apdirs.user_config_dir('pdfebc')`` in the Python interpreter to find the 
   correct directory for your machine.
   Note that you must first import ``appdirs`` for it to be available in the interpreter.

   **Note:** When using a Gmail account, I strongly recommend
   using an `App password`_ instead of the actual account password.

Option 2: Clone the repo and the install with ``pip``
-----------------------------------------------------
If you want the dev version, you will need to clone the repo, as only release versions are uploaded
to PyPi. Unless you are planning to work on this yourself, I suggest going with the release version.

1. Clone the repo with ``git``:
    - ``git clone https://github.com/slarse/pdfebc-web``
2. ``cd`` into the project root directory and install with ``pip``.
    - ``pip install --user .``, this will create a local install for the current user.
    - Or just ``pip install .`` if you use ``virtualenv``.
    - For development, use ``pip install -e .`` in a ``virtualenv``.
3. Install ``Redis`` (used by ``Celery``).
    - This may or may not be available in your package manager, Google it for specifics!
4. Install ``Ghostscript``.
    - Many distributions come with ``Ghostscript`` pre-installed, but you may need to install
      it.
    - Make note of what the binary is called, and enter it in the configuration file
      (see the next step).
5. Currently, you must add the configuration file manually. Please have a look at the
   `sample configuration`_ file for details. Where to put the configuration file is
   machine-dependent, and decided by the ``appdirs`` package. Run 
   ``apdirs.user_config_dir('pdfebc')`` in the Python interpreter to find the correct directory.
   Note that you must first import ``appdirs`` for it to be available in the interpreter.
   **Note:** When using a Gmail account, I strongly recommend
   using an `App password`_ instead of the actual account password.
   
How to run
==========
Assuming everything is installed correctly, running the application is dead simple.

1. Execute ``pdfebc-web-start-celery-redis`` to start up the ``Redis`` server and 4 ``Celery``
   workers. The script will complain if ``Redis`` or ``Celery`` is not installed.
2. Execute ``pdfebc-web runserver -h x.x.x.x -p n`` to run ``pdfebc-web`` while listening
   to address ``x.x.x.x`` and port ``n``. Do note that if you run the server as root,
   for example if you want to run it on a port lower than 1000,
   then ``appdirs`` will likely look for a different configuration directory than if you
   run it as your normal user (because root is a different user).

License
=======
This software is licensed under the MIT License. See the `license file`_ file for specifics.

Contributing
============
I am currently not looking for contributions. At this point, this is a practice project for me,
and even if I were looking for outside help the test suite is nowhere near comprehensive enough
for that yet. Sorry!

.. _App password: https://support.google.com/accounts/answer/185833?hl=en
.. _license file: LICENSE
.. _sample configuration: config.cnf
.. _requirements.txt: requirements.txt
.. _Docs: https://pdfebc-web.readthedocs.io/en/latest/
.. _pdfebc-core: https://github.com/slarse/pdfebc-core
