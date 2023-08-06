
==========
PyMetaWear
==========

.. image:: https://travis-ci.org/hbldh/pymetawear.svg?branch=master
    :target: https://travis-ci.org/hbldh/pymetawear

.. image:: https://coveralls.io/repos/github/hbldh/pymetawear/badge.svg?branch=master
    :target: https://coveralls.io/github/hbldh/pymetawear?branch=master

**PyMetaWear is a community developed Python SDK started by**
`Henrik Blidh <https://github.com/hbldh>`_ **. MbientLab does not provide support for this SDK.**

Python package for connecting to and using
`MbientLab's MetaWear <https://mbientlab.com/>`_ boards.


Capabilities and Limitations
----------------------------

PyMetaWear was previously a wrapper around the
`MetaWear C++ API <https://github.com/mbientlab/Metawear-CppAPI>`_,
providing a more Pythonic interface. In version 0.9.0 it instead becomes
a wrapper around `MetaWear's official Python SDK <https://github.com/mbientlab/MetaWear-SDK-Python>`_,
doing the very same thing. The official SDK handles the actual board
connections and communication while PyMetaWear aims to remove the low level
feeling of interacting with the MetaWear board.


Limitations
+++++++++++

- **Reading data over longer periods of time.** Many users have reported
disconnection problems when trying to use PyMetaWear for long periods.

Installation
------------

Due to a dependency on ``gattlib``, a Python BLE package that is
poorly maintained, MbientLab has `forked it <https://github.com/mbientlab/pygattlib>`
and ships a patched version with its Python SDK. This makes installation of
PyMetaWear require some additional work:

.. code-block:: bash

    $ pip install git+https://github.com/mbientlab/pygattlib.git@master#egg=gattlib
    $ pip install metawear
    $ pip install pymetawear


Documentation
-------------

Available in the `Github pages <https://hbldh.github.io/pymetawear/>`_ of this repository.

Basic Usage
-----------

The MetaWear client can be used in two ways: either as Pythonic
convenience class for handling a MetaWear board or as
a simple communication client governed by the ``libmetawear`` C++ library.

Creating a client, and thus also setting up a Bluetooth connection to the
MetaWear board, is equal for both the two usage profiles:

.. code-block:: python

    from pymetawear.client import MetaWearClient
    c = MetaWearClient('DD:3A:7D:4D:56:F0')

An example: blinking with the LED lights can be done like this with the
convenience methods:

.. code-block:: python

    pattern = c.led.load_preset_pattern('blink', repeat_count=10)
    c.led.write_pattern(pattern, 'g')
    c.led.play()

or like this using the raw ``libmetawear`` shared library:

.. code-block:: python

    from ctypes import byref
    from pymetawear import libmetawear
    from mbientlab.metawear.cbindings import LedColor, LedPreset

    pattern = Led.Pattern(repeat_count=10)
    libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), LedPreset.BLINK)
    libmetawear.mbl_mw_led_write_pattern(c.board, byref(pattern), LedColor.GREEN)
    libmetawear.mbl_mw_led_play(c.board)

Actual addresses to your MetaWear board can be found by scanning, either
directly with ``hcitool lescan`` or with the included ``discover_devices`` method:

.. code-block:: python

    from pymetawear.discover import discover_devices
    out = discover_devices()
    print out
    [(u'DD:3A:7D:4D:56:F0', u'MetaWear'), (u'FF:50:35:82:3B:5A', u'MetaWear')]

See the examples folder for more examples on how to use the ``libmetawear``
library with this client.

Modules
~~~~~~~
All functionality of the MetaWear C++ API is able to be used using the
PyMetaWear client, and some of the modules have had convenience methods
added to simplify the use of them. Below are two list, one of modules which
have had their convenience methods written and one of modules that are
awaiting such focus.

================= =============== =====================
Completed Modules Partial Modules Unimplemented Modules
================= =============== =====================
Accelerometer     GPIO            NeoPixel
Gyroscope                         Color Detector
Haptic                            Humidity
Switch                            iBeacon
LED                               I2C
Barometer
Magnetometer
Temperature
Settings
Ambient Light
================= =============== =====================

=======
History
=======

v0.8.0 (2017-07-04)
-------------------
- Using MetaWear-CppAPI version 0.8.0
- New ownership

v0.7.1 (2017-02-04)
-------------------
- Using MetaWear-CppAPI version 0.7.10
- Sensor fusion module contributed from user m-georgi (#26).
- Fix to magnetometer power preset setting due to
  change in MetaWear-CppAPI (#25).

v0.7.0 (2017-01-13)
-------------------
- Using MetaWear-CppAPI version 0.7.4
- Removed bluepy backend due to it not being fully functional.
- Refactored connection behaviour. Optional autoconnect via keyword.
- Unit test work started with Mock backend.
- Flake8 adaptations.
- Fix for logging bug (#22)
- New examples: Two client setup and complimentary filter sensor fusion (#23).

v0.6.0 (2016-10-31)
-------------------
- Using MetaWear-CppAPI version 0.6.0
- Replaced print-logging with proper logging module usage.
- Removed 64-bit special handling that was no longer needed.

v0.5.2 (2016-10-13)
-------------------
- Temperature Module
- Using Pygatt 3.0.0 (including PR from PyMetaWear contributors)
- Builds on Windows

v0.5.1 (2016-09-15)
-------------------
- Corrections to make it distributable via PyPI.

v0.5.0 (2016-09-15)
-------------------
- Using MetaWear-CppAPI version 0.5.22
- Changed building procedure to handle ARM processors
- Updated requirements to make pygatt default, all others extras
- Bluepy backend implemented and partially working
- BL interface selection for all backends
- Magnetometer module
- Barometer module
- Ambient Light module
- Modifying notification wrappers to accommodate Epoch value in the data.
- High speed sampling for accelerometer and gyroscope

v0.4.4 (2016-04-28)
-------------------
- Updated MetaWear-CppAPI submodule version.
- Removed temporary build workaround.

v0.4.3 (2016-04-27)
-------------------
- Critical fix for switch notifications.
- Updated MetaWear-CppAPI submodule version.
- Now using the new ``setup_metawear`` method.
- Restructured the ``IS_64_BIT`` usage which is still needed.

v0.4.2 (2016-04-27)
-------------------
- Critical fix for timeout in pybluez/gattlib backend.
- Added Gyroscope module.
- Added soft reset method to client.
- Updated examples.
- Updated documentation.

v0.4.1 (2016-04-20)
-------------------
- Cleanup of new modules sensor data parsing.
- Bug fix related to accelerometer module.
- Timeout parameter for client and backends.

v0.4.0 (2016-04-17)
-------------------
- Major refactorisation into new module layout.
- New examples using the new module handling.
- Accelerometer convenience methods shows strange lag still.

v0.3.1 (2016-04-10)
-------------------
- Critical fix for data signal subscription method.
- ``Setup.py`` handling of building made better,
- Documentation improved.

v0.3.0 (2016-04-09)
-------------------
- Major refactoring: all BLE comm code practically moved to backends.
- Backend ``pybluez`` with ``gattlib`` now works well.
- Travis CI problems with Python 2.7 encoding led to
  that we are now building on 2.7.11

v0.2.3 (2016-04-07)
-------------------
- Changed from using ``gattlib`` on its own to using
  ``pybluez`` with ``gattlib``
- Travis CI and Coveralls
- Travis CI deploys documentation to gh-pages.
- Some documentation written.

v0.2.2 (2016-04-06)
-------------------
- Convenience method for switch.
- Sphinx documentation added.
- Docstring updates.

v0.2.1 (2016-04-04)
-------------------
- Refactoring in moving functionality back to client from backends.
- Enable BlueZ 4.X use with ``pygatt``.
- Disconnect methods added.
- Example with switch button notification.

v0.2.0 (2016-04-02)
-------------------
- Two backends: ``pygatt`` and ``gattlib``
- ``pygatt`` backend can be fully initialize, i.e. handles notifications.
- ``gattlib`` backend **cannot** fully initialize, i.e. does **not** handles notifications.

v0.1.1 (2016-03-30)
-------------------
- Fix to support Python 3

v0.1.0 (2016-03-30)
-------------------
- Initial release
- Working communication, tested with very few API options.


