# Home Assistant for leafee mag

Home Assistant (Hass.io) platform for leafee mag.

It supports the `binary_sensor` component and can be used to get status of door or window on your home.


----


## Notice and Limitations

* This is UNOFFICIAL project for the convenience of some users.

    * If you are not Hass.io user or you need reliability, I highly recommend you using the [official service](https://leafee.me/) and the hub.

    * I don't have any relationship with the vendor company (Strobo Inc.) of the leafee mag. Also, "leafee" and "leafee mag" is a trademark of their.

* This software has some limitations and is unstable, because it published under the testing phase.

    * I tested on [Hass.io](https://www.home-assistant.io/hassio/) 0.89.2 + Raspberry Pi 3 Model B.

    * In currently, You can't use with other some components using BLE at the same time.

* I don't any guarantee about this project.


----


## Get Started

### 1. Install the component to your Home Assistant

On Your Home Assistant server (Hass.io):
```
# cd /config

# wget https://github.com/mugifly/homeassistant-leafeemag/archive/master.zip

# unzip master.zip
# rm master.zip

# cp -r homeassistant-leafeemag-master/custom_components/ /config/
# rm -rf homeassistant-leafeemag-master/
```

### 2. Make a configuration

In `configuration.yaml`:
```
binary_sensor:
  - platform: leafeemag
    mac: 'xx:xx:xx:xx:xx:xx'
    name: 'Window of Living'
    device_class: 'door'
    scan_interval: 10
```

* `platform` (**Required**)  -  It must be `leafeemag`.

* `mac` (**Required**)  -  MAC address of your leafee mag.

* `name` (Optional)  - Name of this sensor. In typically it should be name of door or window.

* `device_class` (Optional)  -  Class of this sensor. You can display the icon to the dashboard by setting this value, such as  `door`,  `window` and others. A list of available values is [here](https://www.home-assistant.io/components/binary_sensor/#device-class).

* `scan_interval` (Optional)  -  Interval (seconds) to update the sensor status on Home Assistant. <br>NOTE: Regardless of this setting, reception of sensor status from leafee mag is performed in real-time via Notification system of BLE.

Also it supports multiple sensors. I tested with 6 sensors.

### 3. Restart Home Assistant

After restarting, the sensor will be appeared on your Home Assistant.

It may take few minutes to display the latest status by this component after Home Assistant has started.


----

## FAQ

### `Error occurred during scanning: Unexpected error when scanning: LE Scan ...`

It's no problem.
This component will try again in a few minutes.

### How to check the debug log

Firstly, you need to specifying the log level for this component, in configuration.yaml on Home Assistant.

```
logger:
  default: warning
  logs:
    custom_components.leafeemag.binary_sensor: debug
    pygatt.backends.gatttool.gatttool: info
```

After saving and restarting, then open the "Info" page of your Home Assistant (http://example.com/dev-info) on the browser, and click the "LOAD FULL HOME ASSISTANT LOG" button.


----


## License

```
The MIT License (MIT)
Copyright (c) 2019 Masanori Ohgita
```
