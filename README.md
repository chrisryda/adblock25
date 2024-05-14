# adblock25
A proxy-based adblocker for use with AntennaPod on Waydroid.

## Prerequisites 
You need the following to run adblock25:
 * Python 3.11 or greater
 * Packages from the `requirements.txt` file.
 * Tor proxy
 * The mitmproxy CA certificate installed on the Waydroid device

### Install packages using pip
Run the following command in the root directory of the repository.
```
pip install -r requirements.txt
```
If installing the PySocks package does not work, run the following command in the root directory of the repository:
```
pip install -U 'requests[socks]'
```

### Tor proxy
In the `torrc` file, add the following line and restart the Tor-instance:
```
SOCKSPort 0.0.0.0:9050
```
If you want to use a different port, make sure to update `addon.py` and `write.py` accordingly.

### Install the mitmproxy CA certificate
**Curtesy of user selurvedu in issue [#870](https://github.com/waydroid/waydroid/issues/870).**

Generate the CA certificate by running `mitm.py`. The certificate, called `mitmproxy-ca-cert.pem`, is now located in `~/.mitmproxy`. 
To install the certificate on the Waydroid device, do the following:

Create the `/system/etc/security/cacerts/` directory in the Waydroid overlay file system:
```
$ sudo mkdir -p /var/lib/waydroid/overlay/system/etc/security/cacerts/
```

Find out the hash of the certificate name using an older algorithm as used by OpenSSL before version 1.0.0:
```
$ openssl x509 -subject_hash_old -in mitmproxy-ca-cert.pem | head -1
>> 12gotit34
```

Copy the certificate, renaming it to the hash with `.0` appended, to the created directory and set the proper permissions for it:
```
$ sudo cp mitmproxy-ca-cert.pem /var/lib/waydroid/overlay/system/etc/security/cacerts/12gotit34.0
$ sudo chmod 644 /var/lib/waydroid/overlay/system/etc/security/cacerts/12gotit34.0
```

You may need to restart Waydroid for the changes to take effect. 

## Set the proxy in AntennaPod
In AntennaPod, go to:

Settings &#8594; Downloads &#8594; Proxy

And choose `HTTP` as type. 


Input the IP-address of the Waydroid device (which can be seen by running `ip address show` and finding the `waydroid0` entry, default is `192.168.240.1`) and the port of the proxy (default is `8080`). 
