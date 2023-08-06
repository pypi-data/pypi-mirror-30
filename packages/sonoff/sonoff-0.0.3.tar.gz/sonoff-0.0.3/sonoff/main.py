"""
Python module for controlling Yeelight Sunflower bulbs.

This module exports the Hub and Bulb classes. All bulbs belong to one hub.
"""

import datetime
import logging
import threading
from urllib.request import urlopen
import urllib.parse
import json

TIMEOUT_SECONDS = 4

GET_LIGHTS_COMMAND = "GL,,,,0,\r\n"
BUFFER_SIZE = 8192
UPDATE_INTERVAL_SECONDS = 1
_LOGGER = logging.getLogger(__name__)
DEVICES_PATH = "homekit"


class Hub:
    """
    Yeelight Hub object.

    All Yeelight Sunflower bulbs are attached to the one hub.
    Hub uses TCP sockets to send and receive light data.
    """

    def __init__(self, ip='192.168.0.14', port=1081):
        """Create a hub with given IP and port, establishing socket."""
        self._port = port
        self._ip = ip
        self._socket = None
        self._bulbs = []
        self._lock = threading.Lock()
        # set last updated time to old time so first update will happen
        self._last_updated = datetime.datetime.now() - datetime.timedelta(
            seconds=30)

    def connect(self):
        """Create and connect to socket for TCP communication with hub."""
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(TIMEOUT_SECONDS)
            self._socket.connect((self._ip, self._port))
            _LOGGER.debug("Successfully created Hub at %s:%s :)", self._ip,
                          self._port)
        except socket.error as error:
            _LOGGER.error("Error creating Hub: %s :(", error)
            self._socket.close()

    @property
    def available(self):
        """Check if hub is responsive."""
        return True

    

    def get_data(self):
        """Get current light data as dictionary with light zids as keys."""
        url = "http://" + self._ip + ":" + str(self._port) + "/homekit"

        f = urllib.request.urlopen(url)
        return json.loads(f.read().decode('utf-8'))
        #return bulbs

    def find_index(dicts, key, value):
        class Null: pass
        for i, d in enumerate(dicts):
            if d.get(key, Null) == value:
                return i
        else:
            raise ValueError('no dict with the key and value combination found')

    def get_lights(self):
        """Get current light data, set and return as list of Bulb objects."""
        # Throttle updates. Use cached data if within UPDATE_INTERVAL_SECONDS
        now = datetime.datetime.now()
        if (now - self._last_updated) < datetime.timedelta(
                seconds=UPDATE_INTERVAL_SECONDS):
            # _LOGGER.debug("Using cached light data")
            return self._bulbs
        else:
            self._last_updated = now

        light_data = self.get_data()
        _LOGGER.debug("got: %s", light_data)
        if not light_data:
            return []

        if self._bulbs:
            # Bulbs already created, just update values
            for bulb in self._bulbs:
                # use the values for the bulb with the correct ID
                try:
                    index = self.find_index(light_data,'uid',bulb.uid)
                    values = light_data[index]
                    bulb.state, bulb.outlet, bulb.device, bulb.name, \
                    bulb.uid, bulb.intID = values
                except KeyError:
                    print("exist")
                    pass
        else:
            for light_id in light_data:
                print(light_id)
                self._bulbs.append(Bulb(self, light_id))
        # return a list of Bulb objects
        return self._bulbs


class Bulb:
    """
    Yeelight Bulb object.

    Data and methods for light color and brightness. Requires Hub.
    """

    def __init__(self, hub, light):
        """Construct a Bulb (light) based on current values."""
        self._hub = hub
        self._outlet = light['outlet']
        self._device = light['device']
        self._state = light['state']  # online = 1, offline = 0
        self._name = light['name']
        self._zid = light['uid']
        self._online = 1

    @property
    def zid(self):
        """Return the bulb ID."""
        return self._zid

    @property
    def available(self):
        """Return True if this bulb is online in the current list of bulbs."""
        self.update()
        return self._online

    @property
    def is_on(self):
        """Determine if bulb is on (brightness not zero)."""
        self.update()
        return self._state

    def turn_on(self):
        """Turn bulb on (full brightness)."""
        url = "http://192.168.0.14:1081/v2/devices/100013999a/0/on/sonoff"


        url = "http://" + self._ip + ":" + str(self._port) + "/homekit"

        f = urllib.request.urlopen(url)
        return True

    def turn_off(self):
        """Turn bulb off (zero brightness)."""
        url = "http://192.168.0.14:1081/v2/devices/100013999a/0/off/sonoff"


        f = urllib.request.urlopen(url)
        return True



    def update(self):
        """Update light objects to their current values."""
        bulbs = self._hub.get_lights()
        if not bulbs:
            _LOGGER.debug("%s is offline, send command failed", self._zid)
            self._online = False


x = Hub().get_lights()
