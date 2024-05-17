# adblock25
A proxy-based adblocker for use with AntennaPod on Waydroid.

<br />

## Prerequisites 
You need the following to run adblock25:
 * Python 3.11 or greater
 * Packages from the `requirements.txt` file.
 * The mitmproxy CA certificate installed on the Waydroid device
 * Tor SOCKS proxy

<br />

### Install packages using pip
Run the following command in the root directory of the repository.
```
pip install -r requirements.txt
```
If installing the PySocks package does not work, run the following command in the root directory of the repository:
```
pip install -U 'requests[socks]'
```

<br />

### Install the mitmproxy CA certificate
**Curtesy of user selurvedu in issue [#870](https://github.com/waydroid/waydroid/issues/870).**

Generate the CA certificate by running `mitm.py`. 
The certificate, called `mitmproxy-ca-cert.pem`, is now located in `~/.mitmproxy`. 

To install the certificate on the Waydroid device, do the following:

<br />

Create the `/system/etc/security/cacerts/` directory in the Waydroid overlay file system:
```
sudo mkdir -p /var/lib/waydroid/overlay/system/etc/security/cacerts/
```

<br />

Get the hash of the certificate using an older algorithm as used by OpenSSL before version 1.0.0:
```
openssl x509 -subject_hash_old -in ~/.mitmproxy/mitmproxy-ca-cert.pem | head -1
```
This will output a hash like `12example34`.

<br />

Copy the certificate, renaming it to the hash with `.0` appended, to the created directory and set the proper permissions for it:
```
sudo cp ~/.mitmproxy/mitmproxy-ca-cert.pem /var/lib/waydroid/overlay/system/etc/security/cacerts/12example34.0
sudo chmod 644 /var/lib/waydroid/overlay/system/etc/security/cacerts/12example34.0
```

You may need to restart Waydroid for the changes to take effect. 

<br />

### Tor proxy
To open a Tor SOCKS proxy, you need to edit your `torrc` file.
The location of this file depends on how Tor is installed on your system.
Below are two different options. 

<br />

#### Using tor (AUR)

With the `tor` package from the Arch user repository (AUR), the `torrc` file is located in `/etc/tor` by default.
Add the following line to the `torrc` file:

<br />

```
SOCKSPort 0.0.0.0:9050
```
If you want to use a different port, make sure to update `addon.py` and `write.py` accordingly.

<br />

To restart the Tor-instance, run the following commands:

<br />

```
sudo systemctl stop tor.service
```
```
sudo systemctl start tor.service
```

<br />

#### Using Tor-browser
With Tor-browser, the `torrc` file is located in `Browser/TorBrowser/Data/Tor` in the Tor-browser directory by default.
Add the following line to the `torrc` file:

<br />

```
SOCKSPort 0.0.0.0:9050
```
If you want to use a different port, make sure to update `addon.py` and `write.py` accordingly.

<br />

Restart the instance by exiting and re-opening the Tor-browser.

<br />

## Running adblock25

Run adblock25 via a command line. 

### Run

```
python mitm.py [options]
```

#### Options
|  Option | Description  |
|---|---|
| -h |  Show help message and exit.|
| -p `num`|  Sets the port the proxy binds to. Default is `8080`.|
| -a `file.py`|  Sets the addon that is loaded by `mitm.py`. Default is `addon.py`.|

Available addons:
 * addon.py: Removes ads.
 * write.py: Removes ads and writes processed audio to files.  
 
<br />

## Set the proxy in AntennaPod
With the proxy running, in AntennaPod, go to:

Settings &#8594; Downloads &#8594; Proxy

And choose `HTTP` as type. Input the IP-address of the Waydroid device and the port of the proxy.

The IP-address can be seen by running the command below. 
The address is listed under the `waydroid0` entry. Typically, this address is something like `192.168.240.1`. 

<br />

```
ip address show
```
<br />
