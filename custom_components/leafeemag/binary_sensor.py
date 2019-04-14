"""Support for Mag as Binary Sensor"""

# Import the device class
from homeassistant.components.binary_sensor import PLATFORM_SCHEMA, BinarySensorDevice

# Import constants
# https://github.com/home-assistant/home-assistant/blob/dev/homeassistant/const.py
from homeassistant.const import CONF_NAME, CONF_MAC

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
    vol.Optional(CONF_NAME): cv.string
})

# Initialize the logger
_LOGGER = logging.getLogger(__name__)

# Define constants
BLE_SCAN_TIMEOUT_SEC = 10
BLE_CONNECT_TIMEOUT_SEC = 10
CONNECT_ERROR_RETRY_INTERVAL_SEC = 30
RECONNECT_INTERVAL_SEC = 7200
SENSOR_CHARACTERISTIC_UUID = '3c113000c75c50c41f1a6789e2afde4e'


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup platform."""

    import pygatt
    ble_adapter = pygatt.GATTToolBackend()

    mac_address = config[CONF_MAC]
    name = config.get(CONF_NAME)

    add_devices([MagBinarySensor(ble_adapter, mac_address, name)])

def _on_notification_received_from_mag(instance, handle, value) -> None:
    """This method will be called when the state of Mag changes."""

    if value.decode() == '\x00': # Opened
        instance._set_state(True)
    else: # Closed
        instance._set_state(False)


class MagBinarySensor(BinarySensorDevice):

    def __init__(self, ble_adapter, mac_address, name = None) -> None:
        """Initialzing binary sensor for Mag...."""

        # Initialize
        self._name = name if name != None else mac_address
        self._mac_address = mac_address.upper()
        self._state = None
        self._last_connected_at = 0
        self._ble_adapter = ble_adapter

        # Scan and Subscribe
        self._mag_device = None
        self._scan_and_subscribe()

    @property
    def name(self) -> str:
        """Return the name of this sensor."""
        return self._name

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
            self._scan_and_subscribe()

        elif self._mag_device != None and RECONNECT_INTERVAL_SEC < (time.time() - self._last_connected_at):
            # Reconnect after long time has passed (to keep reliability of connection)
            self._scan_and_subscribe()

        return

    def _scan_and_subscribe(self) -> bool:
        """Find Mag and Subscribe the notification service."""

        # Update time
        self._last_connected_at = time.time()

        # Initialize BLE adapter
        _LOGGER.debug('Initializing BLE adapter...')

        import pygatt
        ble_adapter = pygatt.GATTToolBackend()

        try:
            ble_adapter.start(False)
        except Exception as error:
            _LOGGER.debug('Error occurred during initializing however ignored: %s.', error)

        # Scan BLE devices
        scanned_mag_device = None
        _LOGGER.debug('Scanning BLE devices...')

        try:

            ble_devices = ble_adapter.scan(BLE_SCAN_TIMEOUT_SEC)

            for device in ble_devices:

                if 'address' not in device:
                    continue

                if (device['address'] == self._mac_address):
                    scanned_mag_device = device
                    break

        except Exception as error:
            _LOGGER.error('Error occurred during scanning: %s; Waiting for retry...', error)
            return False

        if scanned_mag_device == None:
            _LOGGER.debug('Mag was not found: %s; Waiting for retry...', self._mac_address)
            return False

        # Connect to device
        _LOGGER.debug('Connecting to Mag... %s', self._mac_address)

        self._mag_device = None
        try:
            self._mag_device = ble_adapter.connect(self._mac_address, BLE_CONNECT_TIMEOUT_SEC, pygatt.BLEAddressType.public)
        except Exception as error:
            _LOGGER.error('Error occurred during connecting: %s; Waiting for retry...', error)
            return False

        # Subscribe to notifications for state changes
        _LOGGER.debug('Subscribing notification... %s', self._mac_address)
        try:
            self._mag_device.subscribe(SENSOR_CHARACTERISTIC_UUID, lambda handle, value: _on_notification_received_from_mag(self, handle, value))
        except Exception as error:
            _LOGGER.error('Error occurred during subscribing: %s; Waiting for retry...', error)
            return False

        # Done
        _LOGGER.info('Ready for detect changing: %s', self._mac_address)
        return True

    def _set_state (self, is_open) -> None:
        """Set state of this sensor."""

        _LOGGER.debug('State of Mag %s has been changed to %s', self._mac_address, is_open)

        # Set state
        self._state = is_open

        # Update time
        self._last_connected_at = time.time()
