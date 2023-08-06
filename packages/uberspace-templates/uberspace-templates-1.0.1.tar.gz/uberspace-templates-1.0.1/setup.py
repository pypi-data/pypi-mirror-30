from setuptools import setup

long_description = """
Uberspace Templates
===================

Setup applications and websites in seconds using this cli with many
templates.

Installation
------------

::

    pip3 install uberspace-templates

Usage
-----

::

    uberspace-templates init template name

    # Example
    uberspace-templates init flask my-application

Templates
~~~~~~~~~

Flask
~~~~~

::

    uberspace-templates init flask my-application

-  Setup of Git deployment (create virtualenv, install requirements.txt,
   copy config.py to project folder)
-  Create daemon and run gunicorn on a free port
-  Setup domain and renew LetsEncrypt
-  Setup reverse proxy

Vue.js
~~~~~~

::

    uberspace-templates init vuejs my-application

-  Setup of Git deployment (install dependencies, build for production,
   copy content to webroot)
-  Setup domain and renew LetsEncrypt
-  Setup Apache configuration

Website
~~~~~~~

::

    uberspace-templates init website my-application

-  Setup of Git deployment (copy content to webroot)
-  Setup domain and renew LetsEncrypt
-  Setup Apache configuration

Made with
=========

-  `click`_ - command line utility

Meta
----

| Lucas Hild - `https://lucas-hild.de`_
| This project is licensed under the MIT License - see the LICENSE file
  for details

.. _click: http://click.pocoo.org
.. _`https://lucas-hild.de`: https://lucas.hild.de
"""

setup(
    name="uberspace-templates",
    version="1.0.1",
    description="Setup applications and websites in seconds using this cli with many templates.",
    long_description=long_description,
    license="MIT",
    author="Lucas Hild",
    author_email="contact@lucas-hild.de",
    url="https://github.com/Lanseuo/uberspace-templates",
    py_modules=["uberspace_templates"],
    install_requires=["click"],
    entry_points="""
        [console_scripts]
        uberspace-templates=uberspace_templates:cli
    """
)
