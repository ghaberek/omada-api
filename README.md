# Omada API

A simple Python wrapper for the [TP-Link Omada Software Controller](https://www.tp-link.com/us/support/download/omada-software-controller/) API.

[![Test Python versions](https://github.com/ghaberek/omada-api/actions/workflows/versions.yml/badge.svg)](https://github.com/ghaberek/omada-api/actions/workflows/versions.yml)

## Usage

Currently this is just the bare-minimum required to log in, get site settings, push site settings, and log out.

```
from omada import Omada

# load our local config file
omada = Omada('omada.cfg')

# or specify the baseurl and site name directly
#omada = Omada(baseurl='https://...', site='Office')

# log into the controller (username and password are in omada.cfg)
omada.login()

# or specify the username and password directly
# omada.login(username='apiuser', password='secretpassword')

# get the site settings
settings = omada.getSiteSettings()

# turn the LEDs off
settings['led']['enable'] = False

# push the settings back
omada.setSiteSettings(settings)

# log out of the controller
omada.logout()
```

## Examples

### [led.py](led.py)

I use this in a cron schedule to turn my site LED setting off at night and back on in the morning.

Turn the LED on:

```
$ python led.py on
led: on
```
Turn the LED off:

```
$ python led.py off
led: off
```

### [clients.py](clients.py), [devices.py](devices.py)

These are simple apps to display similar output to the "Clients" and "Devices" page on the web interface.

```
$ python clients.py
USERNAME            IP ADDRESS      STATUS
00-11-22-33-44-55   192.168.1.123   CONNECTED
...
```

Make sure you have your [Settings](#Settings) file configured correctly for these to work.

## Settings

You can store your controller settings in a configuration file to avoid hard-coding them in your scripts.

Currently supported settings:

- `baseurl` - the base url to the controller
- `site` - the name of the site in the controller (usually `Default`)
- `verify` - set this to `False` to ignore self-signed certificate errors
- `warnings` - set this to `False` to hide urllib3 warnings when `verify=False`
- `verbose` - set this to `True` to force low-level reqeusts to output debugging info
- `username` - the username to log in as
- `password` - the password for the user

### Example

```
[omada]
baseurl = https://omadacontroller.local:8043
site = Default
verify = False
username = apiuser
password = secretpassword
```

## Acknowledgements

For my wife, who asked that I turn off the device LEDs at night. :heart:
