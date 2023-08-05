PyIonic
========================

.. image:: https://readthedocs.org/projects/pyionic/badge/?version=latest
   :target: http://pyionic.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://travis-ci.org/ion-channel/pyionic.svg?branch=master
   :target: https://travis-ci.org/ion-channel/pyionic

.. image:: https://img.shields.io/pypi/v/pyionic.svg
   :target: https://pypi.python.org/pypi/pyionic

PyIonic is a Python library to interact with Ion Channel's API.

Tests
---------------

To setup tests you must first export a valid token for the pyionic test team.::

  export IONCHANNEL_TOKEN=####REDACTED_IONCHANNEL_TOKEN####


Then run::

  pipenv run python setup.py test
