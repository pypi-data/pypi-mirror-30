redis-ratelimit
===============

|Build Status|

A fixed window rate limiting based on Redis

--------------

Requirements
------------

-  Python >= 3.6
-  Redis >= 2

Installation
------------

.. code:: shell

    $ pip install redis-ratelimit

**NB!** redis-ratelimit requires a running Redis server. See `Redis's
quickstart <http://redis.io/topics/quickstart>`__ for installation
instructions.

Getting started
---------------

Assuming you have `Flask <http://flask.pocoo.org/docs/0.12/>`__
installed:

.. code:: python

    from flask import Flask, jsonify
    from redis_ratelimit import ratelimit

    app = Flask(__name__)


    @app.route('/')
    @ratelimit(rate='10/m', key='ccc')
    @ratelimit(rate='2/s', key='ccc')
    def index():
        return jsonify({'status': 'OK'})

This will allow a total of 10 requests in any given minute, but no
faster than 2 requests a second.

Notes
-----

-  `Redis Rate Limiting Pattern
   #2 <https://redis.io/commands/INCR#pattern-rate-limiter-2>`__

License
-------

MIT

.. |Build Status| image:: https://travis-ci.org/r00m/redis-ratelimit.svg?branch=master
   :target: https://travis-ci.org/r00m/redis-ratelimit


