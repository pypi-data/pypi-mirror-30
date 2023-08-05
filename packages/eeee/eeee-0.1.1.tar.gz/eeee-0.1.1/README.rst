****************************
Extremely Easy Event Emitter
****************************

:Info: Extremely Easy Event Emitter.
:Author: Paweł Zadrożny @pawelzny <pawel.zny@gmail.com>


.. image:: https://circleci.com/gh/pawelzny/eeee.svg?style=shield&circle-token=90b9c0d59ae2fc9bf938c6771ada821fd39ce954
   :target: https://circleci.com/gh/pawelzny/eeee
   :alt: CI Status

.. image:: https://readthedocs.org/projects/eeee/badge/?version=latest
   :target: http://eeee.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/eeee.svg
   :target: https://pypi.org/project/eeee/
   :alt: PyPI Repository Status

.. image:: https://img.shields.io/github/release/pawelzny/eeee.svg
   :target: https://github.com/pawelzny/eeee
   :alt: Release Status

.. image:: https://img.shields.io/pypi/status/eeee.svg
   :target: https://pypi.org/project/eeee/
   :alt: Project Status

.. image:: https://img.shields.io/pypi/pyversions/eeee.svg
   :target: https://pypi.org/project/eeee/
   :alt: Supported python versions

.. image:: https://img.shields.io/pypi/implementation/eeee.svg
   :target: https://pypi.org/project/eeee/
   :alt: Supported interpreters

.. image:: https://img.shields.io/pypi/l/eeee.svg
   :target: https://github.com/pawelzny/eeee/blob/master/LICENSE
   :alt: License


Features
========

* Asynchronous Event emitter based on asyncio
* Subscribe any callable handler
* Filter events by Publisher
* Easy enable-disable events on runtime
* Subscribe handlers using decorator


Installation
============

.. code:: bash

    pip install eeee


**Package**: https://pypi.org/project/eeee/


Documentation
=============

Read full documentation at http://eeee.readthedocs.io/en/stable/


Quick Example
=============

.. code:: python

    from eeee import Event, Publisher

    my_event = Event('MyEvent')

    # Subscribe takes publisher instance or name as optional argument.
    # If publisher is defined handler will be triggered only when that
    # particular publisher send a message.
    # Leave empty to listen to all publishers within this event.
    @my_event.subscribe()
    async def custom_handler(message, publisher, event):
        print(message, publisher, event)

    result = await my_event.publish('New message arrived!', Publisher('global'))
