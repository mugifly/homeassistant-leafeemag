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
    name: 'Window of Living'
    mac: 'xx:xx:xx:xx:xx:xx'
    scan_interval: 10
```

Also it supports multiple sensors. I tested using 4 sensors.

### 3. Restart Home Assistant

After restarting, the sensor will be appeared on your Home Assistant.

It may take few minutes to display the latest status by this component after Home Assistant has started.


----

## FAQ

### `Error occurred during scanning: Unexpected error when scanning: LE Scan ...`

It's no problem.
This component will try again in a few minutes.


----


## License

```
The MIT License (MIT)
Copyright (c) 2019 Masanori Ohgita
```
