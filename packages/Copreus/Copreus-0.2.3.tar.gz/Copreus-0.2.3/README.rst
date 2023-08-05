In Greek mythology, Copreus (Κοπρεύς) was King Eurystheus' herald. He
announced Heracles' Twelve Labors.
[`wiki <https://en.wikipedia.org/wiki/Copreus>`__]

This library provides a framework to write device driver for the
raspberry pi that are connected to MQTT.

Thus, Copreus takes commands from the king (MQTT) and tells the hero
(device) what it labors are. Further, Copreus reports to the king
whatever the hero has to tell him.

For Users
=========

Installation Core-Functionality
-------------------------------

Prerequisites for the core functionality are:

::

    sudo apt install python3 python3-pip
    sudo pip3 install RPi.GPIO paho-mqtt pyyaml

Install via pip:

::

    sudo pip3 install copreus

To update to the latest version add ``--upgrade`` as prefix to the
``pip3`` line above.

Install via gitlab (might need additional packages):

::

    git clone git@gitlab.com:pelops/copreus.git
    cd copreus
    sudo python3 setup.py install

This will install the following shell scripts: \* ``copreus`` - alias
for ``copreus_devicemanager`` \*
```copreus_devicemanager`` <https://gitlab.com/pelops/copreus/wikis/devicemanager-devicemanager>`__
- device manager can instantiate several driver \*
```copreus_adc`` <https://gitlab.com/pelops/copreus/wikis/drivers-adc>`__
- analog digital converter via spi \*
```copreus_bme280`` <https://gitlab.com/pelops/copreus/wikis/Drivers-bme_280>`__
- bosch bme280 sensor via SMBus \*
```copreus_dac`` <https://gitlab.com/pelops/copreus/wikis/drivers-dac>`__
- digital analog converter via spi \*
```copreus_dht`` <https://gitlab.com/pelops/copreus/wikis/drivers-dht>`__
- DHT11/DHT22/AM2302 \*
```copreus_epaper`` <https://gitlab.com/pelops/copreus/wikis/drivers-epaper>`__
- Waveshare e-Papers 1.54inch/2.13inch/2.9inch via spi \*
```copreus_input`` <https://gitlab.com/pelops/copreus/wikis/drivers-input>`__
- generic gpio input \*
```copreus_output`` <https://gitlab.com/pelops/copreus/wikis/drivers-output>`__
- generic gpio output \*
```copreus_rotaryencoder`` <https://gitlab.com/pelops/copreus/wikis/drivers-rotaryencoder>`__
- rotary encoder like ky-040

The script cli arguments are: \* '-c'/'--config' - config file
(mandatory) \* '-v' - verbose output (optional) \* '-p'/'--pos' - the
config file for the devicemanager differs from the single driver that it
expects the device configs to be part of 'devices' and not 'device'. If
a devicemanager config should be used with a single driver, this
parameter gives the position of the device in the list of devices
starting with '0'. \* '--version' - show the version number and exit

Additional Prerequisites for Drivers
------------------------------------

Some drivers like ``Input`` and ``Output`` don't need additional
packages. The others need additional prerequisites to be used (they will
be installed without them).

``ADC`` and ``DAC``
~~~~~~~~~~~~~~~~~~~

::

    sudo pip3 install spidev

``bme280``
~~~~~~~~~~

::

    sudo pip3 install smbus2 RPi.bme280

``DHT``
~~~~~~~

::

    sudo apt install build-essential python-dev
    git clone https://github.com/adafruit/Adafruit_Python_DHT.git
    cd Adafruit_Python_DHT
    sudo python3 setup.py install

``epaper``
~~~~~~~~~~

::

    sudo apt install libopenjp2-7 libtiff5
    sudo pip3 install spidev Pillow

Install Everything at Once
--------------------------

::

    sudo apt install python3 python3-pip build-essential python-dev libopenjp2-7 libtiff5
    sudo pip3 install RPi.GPIO paho-mqtt pyyaml spidev Pillow smbus2 RPi.bme280
    git clone https://github.com/adafruit/Adafruit_Python_DHT.git
    cd Adafruit_Python_DHT
    sudo python3 setup.py install
    cd ..
    sudo pip3 install copreus

Further ubuntu and python packages may be needed by example and tests.
For example, ``test_epaper.py`` requires that the ubuntu package
``fonts-freefont-ttf`` is installed.

YAML-Config
-----------

A yaml file must contain two root blocks: \* mqtt - mqtt-address,
mqtt-port, and path to credentials file mqtt-credentials (a file
consisting of two entries: mqtt-user, mqtt-password) \* device or
devices. devices is a list of device entries with two additional
parameters per device: active and name. a device entry contains at least
(driver implementation might add additional ones): type, name, topic-pub
(list of key/value pairs), and topic-sub (list of key/value pairs).

Currently, pyyaml is yaml 1.1 compliant. In pyyaml On/Off and Yes/No are
automatically converted to True/False. This is an unwanted behavior and
deprecated in yaml 1.2. In copreus this autoconversion is removed. Thus,
On/Off and Yes/No are read from the yaml file as strings (see module
baseclasses.mypyyaml).

Examples
~~~~~~~~

More example yaml config files can be found at
`copreus@gitlab/tests <https://gitlab.com/pelops/copreus/tree/master/tests>`__.
Please note that the mqtt credentials must be in a seperate file while
the mqtt config is in the same file as the device configurations.

Config for Driver ``Input``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Can be started with ``copreus_input -c config.yaml -v``. More
information in the
`wiki <https://gitlab.com/pelops/copreus/wikis/drivers-input>`__.

config.yaml:

::

    mqtt:
        mqtt-address: localhost
        mqtt-port: 1883
        mqtt-credentials: ~/credentials.yaml

    device:
        type: input
        pin:  23
        topics-pub:
            button_pressed: /test/button/pressed
            button_state:   /test/button/state
        mqtt-translations:
            button_pressed: PRESSED
            button_state-open: OPEN
            button_state-closed: CLOSED        

credentials.yaml:

::

    mqtt-user: user
    mqtt-password: password

Config for ``DeviceManager``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Can be started with ``copreus -c config.yaml -v``. More information at
`wiki <devicemanager-devicemanager>`__,
`wiki <https://gitlab.com/pelops/copreus/wikis/drivers-input>`__, and
`wiki <https://gitlab.com/pelops/copreus/wikis/drivers-output>`__.

config.yaml:

::

    mqtt:
        mqtt-address: localhost
        mqtt-port: 1883
        mqtt-credentials: ~/credentials.yaml

    devices:
        - name: button1 
          type: input
          pin:  23
          topics-pub:
              button_pressed: /test/button/pressed
              button_state:   /test/button/state
          mqtt-translations:
              button_pressed: PRESSED
              button_state-open: OPEN
              button_state-closed: CLOSED          
        - name: led1
          type: output
          pin: 21
          initially-closed: false
          physical-closed: low      
          topics-sub:
              closed: /test/closed
          mqtt-translations:
              closed-true: ON
              closed-false: OFF          

credentials.yaml:

::

    mqtt:
        mqtt-user: user
        mqtt-password: password

systemd
-------

-  add systemd example.

For Developers
==============

Getting Started
---------------

The project consists of three main packages: \* ``baseclasses`` -
``ADriver`` and additional base- and utilityclasses \* ``devicemanager``
- ``DeviceManager`` and ``DeviceFactory`` \* ``drivers`` - all
implemented driver

Each driver must be a silbiling of ``ADriver``. A new driver must be
added to the ``DeviceFactory``, ``drivers.__init__.py``, ``setup.py``
and ``README.md``. Further, config example must be placed in /tests.

A good starting point is to look at the two generic driver ``Ìnput`` and
``Output`` as well as ``DHT``.

Todos
-----

-  Add more driver
-  SMBus base class
-  Sanity check of yaml config
-  Automated unit tests (instead of manual testing)
-  Better mqtt-credentials handling
-  "Real-world" examples
-  consistent output of drivers in non-verbose operation
-  ...

Misc
----

The code is written for ``python3`` (and tested with python 3.5 on an
Raspberry Pi Zero with Raspbian Stretch).

`Merge requests <https://gitlab.com/pelops/copreus/merge_requests>`__ /
`bug reports <https://gitlab.com/pelops/copreus/issues>`__ are always
welcome.

