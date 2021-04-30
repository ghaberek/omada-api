# Omada API

A simple Python wrapper for the [TP-Link Omada Software Controller](https://www.tp-link.com/us/support/download/omada-software-controller/) API.

## Usage

Currently this is just the bare-minimum required to log in, get site settings, push site settings, and log out.

I use [led.py](led.py) in a cron schedule to turn my site LED setting off at night and back on in the morning.

### Example

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

## Settings

You can store your controller settings in a configuration file to avoid hard-coding them in your scripts.

Currently supported settings:

- `baseurl` - the base url to the controller
- `site` - the name of the site in the controller (usually `Default`)
- `verify` - set this to `False` to ignore self-signed certificate errors
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
