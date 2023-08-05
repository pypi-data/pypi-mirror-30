# WirelessSensorTags  [![Build Status](https://travis-ci.org/sergeymaysak/wirelesstagpy.svg?branch=master)](https://travis-ci.org/sergeymaysak/wirelesstagpy) [![Coverage Status](https://coveralls.io/repos/github/sergeymaysak/wirelesstagpy/badge.svg?branch=master)](https://coveralls.io/github/sergeymaysak/wirelesstagpy?branch=master) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/wirelesstagpy.svg)

A simple python wrapper library for Wireless Sensor Tag platform (http://wirelesstag.net).

Supports getting data for registered by end user sensor tags.
mytaglist.com account credentials are needed to use this lib.
Enabling tags sharing is not required.

Verified with: 
- 13-bit motion/temperature/humidity tags (type 13)
- Water/Moisture tags (type 32)
- ALS Pro tag (type 26)

# Installation

```shell
pip3 install wirelesstagpy
```

# Development notes
See http://wirelesstag.net/apidoc.html for API details.

# Usage

# Fetch all tags

```python

import wirelesstagpy

api = wirelesstagpy.WirelessTags(username='login_email', password='your_password')
sensors = api.load_tags()
for (uuid, tag) in sensors.items():
    print('Loaded sensor: {}, temp: {}, humidity: {} probe taken: {}'.format(
                tag.name, tag.temperature, 
                tag.humidity, tag.time_since_last_update))

```

# Install custom push notifications

Wireless Sensor Tags platforms allows to setup custom url calls for set of specific events.
```python

import wirelesstagpy

api = wirelesstagpy.WirelessTags(username='login_email', password='your_password')
notifications = [
    NotificationConfig('update', {
        'url': 'http://some_local_ip/update_tags',
        'verb': 'POST'
        'disabled': False,
        'nat': True
    })
]

# install notification for tag with id=1 only
succeed = api.install_push_notification(1, notifications, False)

```

# Arm/Disarm sensor monitoring for specific event

Supported events include: motion, temperature, humidity, light
```python

import wirelesstagpy

api = wirelesstagpy.WirelessTags(username='login_email', password='your_password')

# arm humidity monitoring for tag with id 1,
# returned instance is updated SensorTag
sensor = api.arm_humidity(1)

# Disarm it
sensor = api.disarm_humidity(1)

```

# Disclaimer
"Wireless Sensor Tags", "KumoSensor" and "Kumostat" are trademarks of Cao Gadgets LLC,
see www.wirelesstag.net for more information.

I am in no way affiliated with Cao Gadgets LLC.

# Copyright
See [LICENSE](LICENSE)

