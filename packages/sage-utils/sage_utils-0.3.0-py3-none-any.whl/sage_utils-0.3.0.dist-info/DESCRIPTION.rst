sage-utils-python
####################
SDK for Open Matchmaking microservices in Python

Features
========
- Framework agnostic solution
- Easy to write a new extension and use it later with your code
- Base class for implementing AMQP workers
- Register a new microservice in Open Matchmaking platform

Installation
============
This package should be installed using pip: ::

    pip install sage-utils

Example
=======
.. code-block:: python

    from sanic import Sanic
    from sage_utils.extension import BaseExtension


    class CustomExtension(BaseExtension):
        extension_name = app_attribute = 'custom'

        def hello(self, user):
            print("Hello, {}!".format(user))


    app = Sanic(__name__)
    CustomExtension()  # available via `app.custom` or `app.extensions['custom']`
    app.custom.hello('world')  # Hello, world!

License
=======
The sage-utils-python is published under BSD license. For more details read LICENSE_ file.

.. _links:
.. _LICENSE: https://github.com/OpenMatchmaking/sage-utils-python/blob/master/LICENSE

