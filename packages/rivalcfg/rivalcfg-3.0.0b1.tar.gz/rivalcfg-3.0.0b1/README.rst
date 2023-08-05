rivalcfg: Configure SteelSeries gaming mice
===========================================

|Build Status| |PYPI Version| |License| |IRC Freenode #rivalcfg|

rivalcfg is a small CLI utility program that allows you to configure
SteelSeries Rival gaming mice on Linux and Windows (probably works on
BSD and Mac OS too, but not tested).

Supported mice:

-  SteelSeries Rival *(1038:1384)*
-  SteelSeries Rival 100 *(1038:1702)*
-  SteelSeries Rival 300 *(1038:1710)*
-  SteelSeries Rival 300 CS:GO Fade Edition *(1038:1394)*
-  SteelSeries Rival 300 CS:GO Hyperbeast Edition *(1038:171a)*
-  SteelSeries Heroes of the Storm (Sensei Raw) *(1038:1390)*

Experimental support:

-  SteelSeries Rival 310 *(1038:1720)*
-  SteelSeries Rival 500 *(1038:170e)*

If you have trouble running this software, please open an issue on
Github:

-  https://github.com/flozz/rivalcfg/issues

Requirement
-----------

-  Any Linux distribution that use ``udev`` (Debian, Ubuntu, ArchLinux,
   Fedora,...) or Windows
-  `hidapi <https://pypi.python.org/pypi/hidapi/0.7.99.post20>`__

Installation
------------

Prerequisites
~~~~~~~~~~~~~

**Linux:**

Installation require a compilation toolchain and python headers to
compile ``hidapi``. On Debian / Ubuntu, this can be installed with the
following command (as root):

::

    apt-get install build-essential python-dev

**Windows:**

On Windows, you have to install first:

-  Python 3.6 or 2.7: https://www.python.org/
-  Visual C++ 2015 Build Tools:
   http://landinghub.visualstudio.com/visual-cpp-build-tools

Installing From PYPI
~~~~~~~~~~~~~~~~~~~~

Run the following command (as root):

::

    pip install rivalcfg

Installing From sources
~~~~~~~~~~~~~~~~~~~~~~~

Clone the repositiory:

::

    git clone https://github.com/flozz/rivalcfg.git
    cd rivalcfg

Install rivalcfg (as root):

::

    pip install .

**NOTE:** udev rules should be automatically installed, but if setup
fails, you should copy the rules manually:
``cp rivalcfg/data/99-steelseries-rival.rules /etc/udev/rules.d/`` and
then run the ``udevadm trigger`` command.

Archlinux AUR package
~~~~~~~~~~~~~~~~~~~~~

Use package
`rivalcfg-git <https://aur.archlinux.org/packages/rivalcfg-git>`__

CLI
---

::

    Usage: rivalcfg [options]

Main Options:

::

    --version           show program's version number and exit
    -h, --help          show this help message and exit
    -l, --list          print compatible mice and exit

SteelSeries Rival and Rival 300 Options:

::

    -c LOGO_COLOR, --logo-color=LOGO_COLOR
                        Set the logo backlight color (e.g. red, #ff0000,
                        ff0000, #f00, f00, default: #FF1800)
    -e LOGO_LIGHT_EFFECT, --logo-light-effect=LOGO_LIGHT_EFFECT
                        Set the logo light effect (values: 1, 2, 3, 4, breath,
                        steady, default: steady)
    -p POLLING_RATE, --polling-rate=POLLING_RATE
                        Set polling rate in Hz (values: 125, 250, 500, 1000,
                        default: 1000)
    -s SENSITIVITY1, --sensitivity1=SENSITIVITY1
                        Set sensitivity preset 1 (from 50 to 6500 in
                        increments of 50, default: 800)
    -S SENSITIVITY2, --sensitivity2=SENSITIVITY2
                        Set sensitivity preset 2 (from 50 to 6500 in
                        increments of 50, default: 1600)
    -C WHEEL_COLOR, --wheel-color=WHEEL_COLOR
                        Set the wheel backlight color (e.g. red, #ff0000,
                        ff0000, #f00, f00, default: #FF1800)
    -E WHEEL_LIGHT_EFFECT, --wheel-light-effect=WHEEL_LIGHT_EFFECT
                        Set the wheel light effect (values: 1, 2, 3, 4,
                        breath, steady, default: steady)
    -r, --reset         Reset all options to their factory values

SteelSeries Rival 100 Options:

::

    -b BTN6_ACTION, --btn6-action=BTN6_ACTION
                        Set the action of the button under the wheel (values:
                        default, os, default: default)
    -c COLOR, --color=COLOR
                        Set the mouse backlight color (e.g. red, #ff0000,
                        ff0000, #f00, f00, default: #00FFFF)
    -e LIGHT_EFFECT, --light-effect=LIGHT_EFFECT
                        Set the light effect (values: 1, 2, 3, 4, breath,
                        steady, default: steady)
    -p POLLING_RATE, --polling-rate=POLLING_RATE
                        Set polling rate in Hz (values: 125, 250, 500, 1000,
                        default: 1000)
    -s SENSITIVITY1, --sensitivity1=SENSITIVITY1
                        Set sensitivity preset 1 (values: 250, 500, 1000,
                        1250, 1500, 1750, 2000, 4000, default: 1000)
    -S SENSITIVITY2, --sensitivity2=SENSITIVITY2
                        Set sensitivity preset 2 (values: 250, 500, 1000,
                        1250, 1500, 1750, 2000, 4000, default: 2000)
    -r, --reset         Reset all options to their factory values

SteelSeries Rival 300 CS:GO Fade Edition Options:

::

    -b BTN6_ACTION, --btn6-action=BTN6_ACTION
                        Set the action of the button under the wheel (values:
                        default, os, default: default)
    -c LOGO_COLOR, --logo-color=LOGO_COLOR
                        Set the logo backlight color (e.g. red, #ff0000,
                        ff0000, #f00, f00, default: #FF5200)
    -e LOGO_LIGHT_EFFECT, --logo-light-effect=LOGO_LIGHT_EFFECT
                        Set the logo light effect (values: breathfast,
                        breathmed, breathslow, steady, 1, 2, 3, 4, default:
                        steady)
    -p POLLING_RATE, --polling-rate=POLLING_RATE
                        Set polling rate in Hz (values: 125, 250, 500, 1000,
                        default: 1000)
    -s SENSITIVITY1, --sensitivity1=SENSITIVITY1
                        Set sensitivity preset 1 (from 50 to 6500 in
                        increments of 50, default: 800)
    -S SENSITIVITY2, --sensitivity2=SENSITIVITY2
                        Set sensitivity preset 2 (from 50 to 6500 in
                        increments of 50, default: 1600)
    -C WHEEL_COLOR, --wheel-color=WHEEL_COLOR
                        Set the wheel backlight color (e.g. red, #ff0000,
                        ff0000, #f00, f00, default: #FF5200)
    -E WHEEL_LIGHT_EFFECT, --wheel-light-effect=WHEEL_LIGHT_EFFECT
                        Set the wheel light effect (values: breathfast,
                        breathmed, breathslow, steady, 1, 2, 3, 4, default:
                        steady)
    -r, --reset         Reset all options to their factory values

SteelSeries Rival 310 Options (Experimental):

::

    -s SENSITIVITY1, --sensitivity1=SENSITIVITY1
                        Set sensitivity preset 1 (from 100 to 12000 in
                        increments of 100, default: 800)
    -S SENSITIVITY2, --sensitivity2=SENSITIVITY2
                        Set sensitivity preset 2 (from 100 to 12000 in
                        increments of 100, default: 1600)

SteelSeries Rival 500 Options (Experimental):

::

    -c LOGO_COLOR, --logo-color=LOGO_COLOR
                        Set the logo backlight color (e.g. red, #ff0000,
                        ff0000, #f00, f00, default: #FF1800)
    -t COLOR1 COLOR2 SPEED, --logo-colorshift=COLOR1 COLOR2 SPEED
                        Set the logo backlight color (e.g. red aqua 200,
                        ff0000 00ffff 200, default: #FF1800 #FF1800 200)
    -C WHEEL_COLOR, --wheel-color=WHEEL_COLOR
                        Set the wheel backlight color (e.g. red, #ff0000,
                        ff0000, #f00, f00, default: #FF1800)
    -T COLOR1 COLOR2 SPEED, --wheel-colorshift=COLOR1 COLOR2 SPEED
                        Set the wheel backlight color (e.g. red aqua 200,
                        ff0000 00ffff 200, default: #FF1800 #FF1800 200)
    -r, --reset         Reset all options to their factory values

FAQ (Frequently Asked Questions)
--------------------------------

How can I turn the lights off?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can turn the lights off by setting the black color to the lights.

Example with Rival 100:

::

    rivalcfg --color=black

Example with Rival, Rival 300:

::

    rivalcfg --logo-color=black --wheel-color=black

I have a "Permission denied" error, what can I do?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have an error like

::

    IOError: [Errno 13] Permission denied: u'/dev/hidrawXX'

this means that the udev rules have not been installed with the
software. This can be fixed using the following commands (as root):

::

    wget https://raw.githubusercontent.com/flozz/rivalcfg/master/rivalcfg/data/99-steelseries-rival.rules -O /etc/udev/rules.d/99-steelseries-rival.rules

    sudo udevadm trigger

Debug
-----

Rivalcfg uses several environment variable to enable different debug
features:

-  ``RIVALCFG_DEBUG=1``: Enable debug. Setting this variable will allow
   rivalcfg to write debug information to stdout.

-  ``RIVALCFG_DRY=1`` Enable dry run. Setting this variable will avoid
   rivalcfg to write anything to a real device plugged to the computer
   (i any). It will instead simulate the device, so it can be used to
   make test on mice that are not plugged to the computer if used in
   conjunction to the ``RIVALCFG_PROFILE`` variable.

-  ``RIVALCFG_PROFILE=<VendorID>:<ProductID>``: Forces rivalcfg to load
   the corresponding profile instead of the one of the plugged device
   (if any).

-  ``RIVALCFG_DEVICE=<VendorID>:<ProductID>``: Forces rivalcfg to write
   bytes to this device, even if it is not matching the selected
   profile.

**Example: debug logging only:**

::

    $ RIVALCFG_DEBUG=1  rivalcfg --list

**Example: dry run on Rival 300 profile:**

::

    $ RIVALCFG_DRY=1 RIVALCFG_PROFILE=1038:1710  rivalcfg -c ff1800

**Example: using Rival 300 command set on Rival 300 CS:GO Fade Editon
mouse:**

::

    $ RIVALCFG_PROFILE=1038:1710     RIVALCFG_DEVICE=1038:1394    rivalcfg -c ff1800
    # ↑ selects "Rival 300" profile  ↑ but write on the "Rival 300 CS:GO Fade Edition" device

**Example debug output:**

::

    [DEBUG] Rivalcfg 2.5.3
    [DEBUG] Python version: 2.7.13
    [DEBUG] OS: Linux
    [DEBUG] Linux distribution: Ubuntu 17.04 zesty
    [DEBUG] Dry run enabled
    [DEBUG] Forced profile: 1038:1710
    [DEBUG] Targeted device: 1038:1710
    [DEBUG] Selected mouse: <Mouse SteelSeries Rival 300 (1038:1710:00)>
    [DEBUG] Mouse._device_write: 00 08 01 FF 18 00
    [DEBUG] Mouse._device_write: 00 09 00

Changelog
---------

-  **2.6.0:** Add CS:GO Hyperbeast Edition support (thanks
   @chriscoyfish, #33)
-  **2.5.3:** Minor typo fixes for cli (thanks @chriscoyfish, #31)
-  **2.5.2:** Fixes Rival 300 with updated firmware not working (#5,
   #25, #28, special thanks to @Thiblizz)
-  **2.5.1:** Fixes mouse not recognized on system with more than 10 USB
   busses (#21)
-  **2.5.0:** Rival 300 CS:GO Fade Edition support (thanks @Percinnamon,
   #20)
-  **2.4.4:** Improves debug options
-  **2.4.3:** Fixes an issue with Python 3 (#8)
-  **2.4.2:** Fixes a TypeError with Python 3 (#7)
-  **2.4.1:** Help improved
-  **2.4.0:** Python 3 support (#4)
-  **2.3.0:**
-  Rival and Rival 300 support is no more experimental
-  Improves the device listing (--list)
-  Fixes bug with color parsing in CLI (#1)
-  Fixes unrecognized devices path on old kernel (#2)
-  **2.2.0:** Experimental Rival 300 support
-  **2.1.1:** Includes udev rules in the package and automatically
   install the rules (if possible)
-  **2.1.0:** Experimental Original Rival support
-  **2.0.0:** Refactored to support multiple mice
-  **1.0.1:** Fixes the pypi package
-  **1.0.0:** Initial release

.. |Build Status| image:: https://travis-ci.org/flozz/rivalcfg.svg?branch=master
   :target: https://travis-ci.org/flozz/rivalcfg
.. |PYPI Version| image:: https://img.shields.io/pypi/v/rivalcfg.svg
   :target: https://pypi.python.org/pypi/rivalcfg
.. |License| image:: https://img.shields.io/pypi/l/rivalcfg.svg
   :target: https://github.com/flozz/rivalcfg/blob/master/LICENSE
.. |IRC Freenode #rivalcfg| image:: https://img.shields.io/badge/IRC_Freenode-%23rivalcfg-brightgreen.svg
   :target: http://webchat.freenode.net/?channels=rivalcfg
