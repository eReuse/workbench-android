Basics adb commands
===================

What you must know about adb.


Install adb
-----------------

To install it for `ubuntu`_ or `debian`_ use the following command::

    sudo apt update && sudo apt install android-tools-adb

.. _ubuntu: https://packages.ubuntu.com/bionic/android-tools-adb
.. _debian: https://packages.debian.org/stretch/android-tools-adb

List devices connected
----------------------

To list current devices detected use the following command::

    adb devices

You will get a list of devices in a rows, if you can't see your device
means it's not detected or not connected.

The first column of the list (for row) will be the serial number of the
device, the second column will be the current state of the device.
