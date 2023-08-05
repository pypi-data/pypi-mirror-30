samsung_print
=============

This was merged with `PySyncThru <https://github.com/nielstron/pysyncthru>`_ and is no longer maintained.

Python API for interacting with printers from Samsung. Mainly to get the
details about the different media levels.

Installation
------------

The module is available from the `Python Package Index <https://pypi.python.org/pypi>`_.

.. code:: bash

    $ pip3 install samsung_print

Usage
-----

.. code:: python

    import asyncio

    import aiohttp

    from samsung_print import Printer

    IP_PRINTER = '192.168.1.200'


    @asyncio.coroutine
    def main():
        with aiohttp.ClientSession() as session:
            printer = Printer(IP_PRINTER, loop, session)
            yield from printer.async_get_data()

            print("Printer status:", printer.status('hrDeviceStatus'))


    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

The file ``example.py`` contains further options about how to use this module.

Supported printer
-----------------

``samsung_print`` was tested with the following printer:

- C410W

Development
-----------

For development is recommended to use a ``venv``.

.. code:: bash

    $ python3.6 -m venv .
    $ source bin/activate
    $ python3 setup.py develop

License
-------

``samsung_print`` is licensed under MIT, for more details check LICENSE.
