BrickFTP
=======

|PyPI| |Python Versions| |Build Status|

Python Client for BrickFTP API (https://developers.brickftp.com/).

Installation
------------

To install brickftp, simply:

.. code:: bash

    pip install brickftp

How To Use
----------

Initialise the client
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from brickftp import BrickFTP
    client = BrickFTP(
        username='bob@example.com',
        password='password123',
        subdomain='subdomain',
    )

Available methods
~~~~~~~~~~~~~~~~~

NOTE: For each client method, if there is a negative response from the API then ``BrickFTPError`` will raise.

List the contents of a folder
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    client.dir('/some_remote/path')

Upload a file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Upto 5MB supported by the client at this time.

.. code:: python

    client.upload(upload_path='/some/path.txt', local_path='path.txt)

Download a file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    client.download_file(remote_path='/some/path.txt', local_path='path.txt)

Delete a file or folder
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

NOTE: Deletes recursively through subdirectories.

.. code:: python

    client.delete('/some_remote/path')

Requirements
------------

::

    1. Python 3.6+
    2. See requirements.txt

Running the tests
-----------------

Set the environment variables: ``BRICK_FTP_USER``, ``BRICK_FTP_PASS``, ``BRICK_FTP_SUBDOMAIN``.

Note: Running the tests against a BrickFTP user will wipe all data on their account.

.. code:: bash

    pip install -r requirements-test.txt
    pytest

.. |PyPI| image:: https://img.shields.io/pypi/v/brickftp.svg
   :target: https://pypi.python.org/pypi/brickftp
.. |Python Versions| image:: https://img.shields.io/pypi/pyversions/brickftp.svg
   :target: https://pypi.python.org/pypi/brickftp
.. |Build Status| image:: https://travis-ci.org/Usio-Energy/BrickFTP.png?branch=master
   :target: https://travis-ci.org/Usio-Energy/BrickFTP
