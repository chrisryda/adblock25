from mitmproxy.tools.main import mitmdump
import requests
import os

def get_tor_session():
    session = requests.session()
    session.proxies = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}
    return session

session = get_tor_session()
ip = session.get("http://httpbin.org/ip").text.split("\"")
print(f"Using IP-address {ip[3]} for upstream connections")

mitmdump(args=[
    "-s", "addon.py",
    "--set", f"connect_adr={ip[3]}"
])
