PyLinkbot3
==========

PyLinkbot - A Python package for controlling Barobo Linkbots
Contact: David Ko <david@barobo.com>

Linkbots are small modular robots designed to play an interactive role in
computer science and mathematics curricula. More information may be found at
http://www.barobo.com .

Requirements
------------

This package makes extensive use of asyncio which is only available in Python
3.5 and greater.

This package also requires protobuf>=3.0.0b2 and PySfp.

Installation
------------

The recommended way to install this package is through setuptools utilities,
such as "easy_install" or "pip". For example:

    easy_install3 PyLinkbot3

or

    pip3 install PyLinkbot3

Usage Options
-------------

This version of PyLinkbot3 can communicate with old SFP based baromeshd daemons
and new websockets based daemons. By default, the library will search for an
SFP based daemon located at localhost:42000. The following environment
variables control this library's behavior:

LINKBOT_USE_SFP=1 # Makes PyLinkbot use the old SFP transport instead of
                  # WebSockets.
LINKBOT_DAEMON_HOSTPORT="hostname:port" # Makes PyLinkbot use the specified
    # host:port as its daemon. For instance, if you want to use the daemon
    # running on a local linkbot-hub, set this environment variable to the
    # hostname and port of the linkbot hub.

CHANGES
=======

Version 3.1.17
--------------
* Removed PySfp requirement.

Version 3.1.16
--------------
* Added CLinkbot.turn_left_nb() and CLinkbot.turn_right_nb()
* Gave "radius" and "tracklength" arguments for turn_* functions default values
  of 1.75 and 3.7, respectively

Version 3.1.15
--------------
* Added CLinkbot.turn_left() and CLinkbot.turn_right()
* Fixed bug in move_wait() waiting for long running movements

Version 3.1.14
--------------
* Added CLinkbot class.

Version 3.1.13
--------------
* Added way to accept new robot connections by reading serial ID's from an
  environment variable.

Version 3.1.12
--------------
* Added method to reset peripherals on disconnect.

Version 3.1.11
--------------
* Added drive_* functions to CLinkbot class, based on C-STEM API.

Version 3.1.10
--------------
* Fixed bug where calling linkbot3.config() resets all config settings

Version 3.1.9
-------------
* Added encoder event callbacks to CLinkbot
* Changed PREX plotting to use plotly.js
* Fixed bug setting daemon hostport via environment variable

Version 3.1.8
-------------
* Changed serial ID in all code snippets to "ZRG6"
* Fixed bug where _util.Config() sometimes ignores environment variables
* Added top-level "linkbot" package; can now do "import linkbot". 

Version 3.1.7
-------------
* Added Daemon.ping() method

Version 3.1.6
-------------
* Fixed bug in begin_move()

Version 3.1.5
-------------
* Fixed bug when calling Linkbot functions from within Linkbot event handlers
* Fixed syntax error in Motor.move_wait()

Version 3.1.4
-------------
* Getting serial ID's retrieves it from the robot rather than relying on
  previously saved value


Version 3.1.3
-------------
* Removed debugging message
* Fixed blocking Linkbot event handlers stopping the World.

Version 3.1.2
-------------
* Added "timeout" config option to set the default timeout for Linkbot
  communications.

Version 3.1.1
-------------
* Pass linkbot3.scatter_plot() arguments directly to pyplot
* Fixed bugs, syntax errors in CLinkbot

Version 3.1.0
-------------

* Added "CLinkbot" API, which is styled more closely after the C-STEM C++ Linkbot API.
* Added internal support for the Prex communications channel for remote execution.

Version 3.0.7
-------------

* Added the linkbot3.scatter_plot() function
* Increased default robot timeout to 30 seconds
* Fixed "Dongle not found" error message
* Added Linkbot.reboot()

Version 3.0.6
-------------

* Fixed daemon connection process
* Added some more documentation snippets

Version 3.0.5
-------------

* Added Motors.set_powers()
* Fixed motor event handler

Version 3.0.4
-------------

* Internal bugfixes

Version 3.0.3
-------------

* Made everything compatible with Python 3.4.2
* Added Motor.angle()
* Added Led.set_color_code()
* Added Linkbot.disconnect()
* Updated plot demo

Version 3.0.2
-------------

* Added daemon object

Version 3.0.1
-------------

* Fixed syntax error

