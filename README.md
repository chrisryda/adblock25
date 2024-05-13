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
Generate the CA certificate by running `mitm.py`. The certificate, called `mitmproxy-ca-cert.pem`, is now located in `~/.mitmproxy`. 
Installing the certificate on the Waydroid-device is somewhat tricky, 
do the following:

Find out the hash of the certificate name using an older algorithm as used by OpenSSL before version 1.0.0:
```
$ openssl x509 -subject_hash_old -in mitmproxy-ca-cert.pem | head -1
>> 12gotit34
```



