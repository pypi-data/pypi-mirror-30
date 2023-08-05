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

Example
---------------

Install PyIonic:

  pip install pyionic

Set the IONCHANNEL_SECRET_KEY:

  export IONCHANNEL_SECRET_KEY=####IONCHANNEL_SECRET_KEY####

Write code:

.. code-block:: python

  from pyionic import core
  vuln = core.Vulnerability()
  vulnerabilities = vuln.get_vulnerabilities('python', '3.4')
  print('%s total vulnerabilities found.' % vulnerabilities['meta']['total_count'])

Run code:

  python test.py
  
  7 total vulnerabilities found.

Tests
---------------

To setup tests you must first export a valid token for the pyionic test team:

  export IONCHANNEL_SECRET_KEY=####IONCHANNEL_SECRET_KEY####


Then run:

  pipenv run python setup.py test
