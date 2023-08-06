========================================
Carillon - ultra simple keyboard layouts
========================================

**Carillon** is a simple GTK3 application for switching your keyboard layout.
If offers a basic systray icon and menu for switching between a set defined
manually.

I created this because there aren't that many applications like this out there
for light desktop environments such as Openbox et al.

Quick Start
===========

This assumes you have a modern Python installation available (Python 2.7+ or
3.4+). To install, get via pip:

.. code:: console

    $ pip install carillon

Now run the command ``carillon``.

Configuration
=============

Carillon looks for a YAML configuration file named ``default.yml`` in a number
of locations and uses the first match:

- current working directory
- XDG config directory e.g. ``~/.config/carillon``
- ``/etc/carillon/conf.d``
- ``/etc/carillon``
- directory of package install

This YAML file defines a map of possible keyboard layouts and the selected
layout. For example:

.. code:: yaml

    ---
    # map of keyboard layouts with unique key name for each
    keyboards:
      # Irish keyboard with Macintosh variant
      en_mac_ie:
        name: English Mac (IE)
        icon: ie.png
        variant: mac
        model: pc105
        layout: gb
      # International US English layout
      en_us:
        name: English (US)
        icon: us.png
        model: pc105
        layout: us

    # Default selected on startup is Irish keyboard
    selected: en_mac_ie

