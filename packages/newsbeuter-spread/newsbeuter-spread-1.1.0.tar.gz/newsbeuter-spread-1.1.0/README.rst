newsbeuter-spread
=================

.. image:: https://badge.fury.io/py/newsbeuter-spread.png
    :target: https://badge.fury.io/py/newsbeuter-spread

.. image:: https://travis-ci.org/narfman0/newsbeuter-spread.png?branch=master
    :target: https://travis-ci.org/narfman0/newsbeuter-spread

Web frontend for newsbeuter db. Read content and mark as read. Own yer own data! (he said with pitchfork)

Installation
------------

Install via pip::

    pip install newsbeuter-spread

Usage
-----

    newsbeuter-spread help

Start the server with::

    $ export FLASK_APP=newsbeuter_spread/app.py
    $ flask run
    * Running on http://127.0.0.1:5000/

Then navigate to the above url!

You might install gunicorn and run using supervisor. In that case, run with::

    gunicorn newsbeuter_spread.app:app -b 0.0.0.0:5000

Development
-----------

Install all the testing requirements::

    pip install -r requirements_test.txt

Run tox to ensure everything works::

    make test

You may also invoke `tox` directly if you wish.

License
-------

Copyright (c) 2017 Jon Robison

See LICENSE for details
