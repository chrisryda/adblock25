# adblock25
A proxy-based adblocker for use with AntennaPod on Waydroid.

## Prerequisites 
You need the following to run adblock25:
 * Python 3.11 or greater
 * Packages from the `requirements.txt` file.
 * Tor proxy
 * The mitmproxy CA certificate installed on the Waydroid-device

### Install packages using pip
Run the following command in the root directory of the repository.
```
pip install -r requirements.txt
```

## Tor proxy
In the `torrc` file, add the following line:
```
SOCKSPort 0.0.0.0:9050
```
If you want to use a different port, make sure to update `addon.py` and/or `write.py` accordingly.

## Install the mitmproxy CA certificate
This is where it gets a bit tricky. 

