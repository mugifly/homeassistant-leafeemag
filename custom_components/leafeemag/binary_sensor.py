"""Support for Mag as Binary Sensor"""

# Import the device class
from homeassistant.components.binary_sensor import PLATFORM_SCHEMA, BinarySensorDevice

# Import constants
# https://github.com/home-assistant/home-assistant/blob/dev/homeassistant/const.py
from homeassistant.const import CONF_DEVICE_CLASS, CONF_MAC, CONF_NAME

# Import classes for validation
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

# Import class for byte comparison
import ast

# Import class for interval check
import time

# Import the logger for debugging
import logging

# Define the required pypi package
REQUIREMENTS = ['pygatt[GATTTOOL]==3.2.0']

# Define the validation of configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_MAC): cv.string,
    vol.Optional(CONF_DEVICE_CLASS, default='window'): cv.string,
    vol.Optional(CONF_NAME): cv.string
})

# Initialize the logger
_LOGGER = logging.getLogger(__name__)

# Define constants
BLE_CONNECT_TIMEOUT_SEC = 10
BLE_READ_TIMEOUT_SEC = 5
CONNECT_ERROR_RETRY_INTERVAL_SEC = 30
RECONNECT_INTERVAL_SEC = 7200
SENSOR_CHARACTERISTIC_UUID = '3c113000-c75c-50c4-1f1a-6789e2afde4e'


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup platform."""

    import pygatt
    ble_adapter = pygatt.GATTToolBackend()

    mac_address = config[CONF_MAC]

    device_class = config.get(CONF_DEVICE_CLASS)
    name = config.get(CONF_NAME)

    add_devices([MagBinarySensor(ble_adapter, mac_address, device_class, name)])

def _on_notification_received_from_mag(instance, handle, value) -> None:
    """This method will be called when the state of Mag changes."""

    instance._set_state_by_received_bytearray(value)


class MagBinarySensor(BinarySensorDevice):

    def __init__(self, ble_adapter, mac_address, device_class, name = None) -> None:
        """Initialzing binary sensor for Mag...."""

        # Initialize
        self._ble_adapter = ble_adapter
        self._mac_address = mac_address.upper()
        self._device_class = device_class
        self._name = name if name != None else mac_address
        self._state = None
        self._last_connected_at = 0

        # Scan and Subscribe
        self._mag_device = None
        self._connect_and_subscribe()

    @property
    def name(self) -> str:
        """Return the name of this sensor."""
        return self._name

    @property
    def device_class(self):
        """Return the device class of this sensor."""
        return self._device_class

    @property
    def is_on(self) -> bool:
        """Return true if this sensor is on."""
        return self._state

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this sensor."""
        return 'lmag_' + self._mac_address

    def update(self) -> None:
        """Not update the state in here, because the state will be updated by notification from the Mag."""

        if self._mag_device == None and CONNECT_ERROR_RETRY_INTERVAL_SEC < (time.time() - self._last_connected_at):
            # Retry connection
            self._connect_and_subscribe()

        elif self._mag_device != None and RECONNECT_INTERVAL_SEC < (time.time() - self._last_connected_at):
            # Reconnect after long time has passed (to keep reliability of connection)
            self._connect_and_subscribe()

        return

    def _connect_and_subscribe(self) -> bool:
        """Connect to Mag and Subscribe the notification service."""

        # Update time
        self._last_connected_at = time.time()

        # Disconnect from device if necessary
        self._disconnect();

        # Initialize BLE adapter
        _LOGGER.debug('Initializing BLE adapter...')

        try:
            self._ble_adapter.start(False)
        except Exception as error:
            _LOGGER.debug('Error occurred during initializing: %s; However ignored.', error)

        # Connect to device
        _LOGGER.debug('Connecting to Mag... %s', self._mac_address)
        self._mag_device = None

        from pygatt import BLEAddressType

        try:
            self._mag_device = self._ble_adapter.connect(self._mac_address, BLE_CONNECT_TIMEOUT_SEC, BLEAddressType.public)
        except Exception as error:
            _LOGGER.error('Error occurred during connecting to %s: %s; Waiting for retry...', self._mac_address, error)
            return False

        # Get latest state
        _LOGGER.debug('Getting latest state... %s', self._mac_address)

        try:

            value = self._mag_device.char_read('3c113000-c75c-50c4-1f1a-6789e2afde4e', BLE_READ_TIMEOUT_SEC)
            self._set_state_by_received_bytearray(value)

        except Exception as error:
            _LOGGER.debug('Error occurred during getting latest state from %s: %s; However ignored.', self._mac_address, error)

        # Subscribe to notifications for state changes
        _LOGGER.debug('Subscribing notification... %s', self._mac_address)

        try:
            self._mag_device.subscribe(SENSOR_CHARACTERISTIC_UUID, lambda handle, value: _on_notification_received_from_mag(self, handle, value))
        except Exception as error:
            _LOGGER.error('Error occurred during subscribing with %s: %s; Waiting for retry...', self._mac_address, error)
            return False

        # Done
        _LOGGER.info('Ready for detect changing: %s', self._mac_address)
        return True

    def _disconnect(self) -> None:
        """Disconnect from Mag."""

        if (self._mag_device == None):
            return

        _LOGGER.debug('Disconnecting from Mag... %s', self._mac_address)

        try:
            self._mag_device.disconnect()
        except Exception as error:
            _LOGGER.debug('Error occurred during disconnecting: %s; However ignored.', error)

    def _set_state_by_received_bytearray (self, received_bytearray) -> None:
        """Set state of this sensor by received sensor value."""

        is_open = None;
        if received_bytearray.decode() == '\x00': # Opened
            is_open = True
        else: # Closed
            is_open = False

        _LOGGER.debug('State of Mag %s has been changed to %s', self._mac_address, is_open)

        # Set state
        self._state = is_open

        # Update time
        self._last_connected_at = time.time()
