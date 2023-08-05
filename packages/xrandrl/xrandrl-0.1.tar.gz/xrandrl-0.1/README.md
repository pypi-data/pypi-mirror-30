# xrandrl

Show names of outputs available to the X server.

This script uses python's ctypes library to access *libX11* and *libXrandr*.

## Requirements

```{sh}
sudo apt-get install python3 libx11-dev libxrandr-dev
```

## Installation

```{sh}
$ pip3 install --user --upgrade git+https://github.com/fphammerle/xrandrl
```

## Usage

```
xrandrl [-h] [-c] [-d] [-e]

optional arguments:
  -c, --connected  connected only
  -d, --disabled   disabled only (does not imply --connected)
  -e, --enabled    enabled only (does not imply --connected)
  -h, --help       show help message and exit
```

### Examples

```{sh}
$ xrandrl --connected
eDP2
DP2-1
DP2-2

$ xrandrl --enabled
eDP2
DP2-2

$ xrandrl --connected --disabled
DP2-1

$ xrandrl
eDP2
DP1
DP2
DP2-1
DP2-2
DP2-3
HDMI1
HDMI2
VGA1
VIRTUAL1
eDP-1-1
DVI-D-1-1
```
