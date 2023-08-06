akeyra :cherry\_blossom:
========================

Agent for `Sakeyra <https://github.com/LaMethode/sakeyra>`__

|Python version| |PyPI version| |Build Status|

|JWT|

What is it?
-----------

| Akeyra is the client-side of Sakeyra.
| It serves the purpose of creating/updating ``~/.ssh/authorized_keys``
| It also create users that don't exist on your server but that are in
  the key-bundle.

How to install ?
----------------

Use Pip ``pip install akeyra``

How to use it?
--------------

| You have to fill the configuration file (see below) to connect to your
  SAKman Server.
| Then you just have to run ``akeyra`` as root.
| Make sure you have a Cron somewhere to update as frequently as
  possible.

Options
-------

usage: akeyra [-h] [-H HOST] [-E ENV] [-K KEY] [-P PROXY] [-F FILE] [-D]

You can provide all informations in CLI, use the basic configfile
(/etc/akeyra.cfg), or an alternative one. If nothing is passed by CLI,
then the basic configfile will be used.

CLI > CLI-File > base file

optional arguments: \* -h, --help show this help message and exit \* -H
HOST, --host HOST Key Server \* -E ENV, --env ENV Environment \* -K KEY,
--key KEY Secret key \* -P PROXY, --proxy PROXY Proxy \* -F FILE, --cnf
FILE Alt Conffile \* -D, --dry Dry run

If you need to use a proxy, you either set environment variable like
http\_proxy or use proxy in the configfile.

Configuration file ``/etc/akeyra.cfg``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    [agent]
    host =
    key =
    environment =
    proxy =

Format between Akeyra and Sakeyra (decode)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: json

    {
      "environment": "rec",
      "users": [
        {"user1": {"email": "userkey1@test.com", "name": "userkey1", "pubkey": "laclepubliquedeuserkey1"}},
        {"user2": {"email": "userkey2@test.com", "name": "userkey2", "pubkey": "laclepubliquedeuserkey2"}}
        ],
        "pub_date": "2017-10-18T17:15:46.799689"
      }

.. |Python version| image:: https://img.shields.io/pypi/pyversions/akeyra.svg
   :target: https://img.shields.io/pypi/pyversions/akeyra.svg
.. |PyPI version| image:: https://img.shields.io/pypi/v/akeyra.svg
   :target: https://img.shields.io/pypi/v/akeyra.svg
.. |Build Status| image:: https://img.shields.io/travis/LaMethode/akeyra.svg?branch=master
   :target: https://img.shields.io/travis/LaMethode/akeyra
.. |JWT| image:: https://jwt.io/assets/badge-compatible.svg
   :target: https://jwt.io/
