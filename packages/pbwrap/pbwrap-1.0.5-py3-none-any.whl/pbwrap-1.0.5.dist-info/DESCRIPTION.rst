Pastebin API wrapper for Python (pbwrap)
========================================

|PyPI version| |Build Status| |Coverage Status|

    | **Python API wrapper for the Pastebin Public API.
      Lifetime pro endpoints are not yet supported!**
    | **Only *Python 3* supported!**

Documentation
-------------

| This wrapper is based on **Pastebin** API read their Documentation
  `**here.**`_
| for extra information and usage guide.

Usage
~~~~~

For a full list of the methods offered by the package `**Read.**`_

Quickstart
^^^^^^^^^^

Import and instantiate a Pastebin Object.

.. code:: Python

    from pbwrap import Pastebin

    pastebin = Pastebin(api_dev_key)

Examples
~~~~~~~~

Get User Id
'''''''''''

Returns a string with the user_id created after authentication.

.. code:: Python

    user_id = pastebin.authenticate(username, password)

Get Trending Pastes details
'''''''''''''''''''''''''''

Returns a list containing Paste objects of the top 18 trending Pastes.

.. code:: Python

    trending_pastes = pastebin.get_trending()

Type models
~~~~~~~~~~~

Paste
^^^^^

| Some API endpoints return paste data in xml format the wrapper either
  converts them in a python dictionary format
| or returns them as Paste objects which contain the following fields:

-  **key**
-  **date** in ***UNIXTIME***
-  **title**
-  **size**
-  **expire_date**
-  **private**
-  **format_short**
-  **format_long**
-  **url**
-  **hits**

License
-------

pbwrap is released under `**MIT License**`_

.. _**here.**: https://pastebin.com/api
.. _**Read.**: http://pbwrap.readthedocs.io/en/latest/
.. _**MIT License**: ./LICENSE

.. |PyPI version| image:: https://badge.fury.io/py/pbwrap.svg
   :target: https://badge.fury.io/py/pbwrap
.. |Build Status| image:: https://travis-ci.org/Mikts/pbwrap.svg?branch=master
   :target: https://travis-ci.org/Mikts/pbwrap
.. |Coverage Status| image:: https://coveralls.io/repos/github/Mikts/pbwrap/badge.svg
   :target: https://coveralls.io/github/Mikts/pbwrap


