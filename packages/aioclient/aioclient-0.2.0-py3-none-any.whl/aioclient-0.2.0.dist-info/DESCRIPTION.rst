aioclient
=========

*An async web client for humans*

Installation
------------

.. code:: sh

    pip install aioclient

Usage
-----

.. code:: python

    import aioclient

    async def get_example():
        status, headers, body = await aioclient.get('https://www.example.com/')
        print(body)

Changelog
---------

v0.1.0
~~~~~~

-  GET requests return ``status, headers, body`` tuples

v0.2.0
~~~~~~

-  Support OPTIONS, HEAD, POST, PUT, PATCH, and DELETE requests
-  Deserialize text/xml responses as XML ElementTree


