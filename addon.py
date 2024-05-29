import requests
from mitmproxy import http
import logging

class AdStripper:
    def __init__(self):
        self.tor_port = 9050
        self.session = self.get_tor_session()
        self.delta = 2**13
        self.url = ""
        self.route = {}
        self.stripped = {}
    
    def get_tor_session(self):
        session = requests.session()
        session.proxies = {'http': f'socks5h://127.0.0.1:{self.tor_port}', 'https': f'socks5h://127.0.0.1:{self.tor_port}'}
        return session
    
    def request(self, flow: http.HTTPFlow) -> None:
        origin = self.get_origin(flow.request.url)
        if origin and origin in self.stripped.keys():
            try:
                bs = int(flow.request.headers["Range"].split("=")[1][:-1])
                d = self.stripped[origin][bs:]
            except KeyError:
                bs = None
                d = self.stripped[origin]
            
            status_code = 206 if bs else 200
            logging.info("Found stripped file, sending response")
            flow.response = http.Response.make(
                status_code,
                d,  
                {"Content-Length": str(len(d))}
            )
                

    def response(self, flow: http.HTTPFlow) -> None:
        if flow.response.status_code == 302:
            self.update_route(flow.request.url, flow.response.headers["location"])
            return
        
        if "no content" in str(flow.response).lower():
            return
        
        try:
            content_type = flow.response.headers["Content-Type"]
        except KeyError:
            return
        
        if flow.response.status_code == 206 and "audio" in content_type:
            try:
                bs = int(flow.request.headers["range"].split("=")[1][:-1])
            except KeyError:
                logging.info("Could not determine skip, serving original file")
                return  
                                 
            logging.info(flow.response)
            self.url = self.get_origin(flow.request.url)
            if not self.url:
                self.url = flow.request.url

            if self.url in self.stripped.keys():
                d = self.stripped[self.url][bs:]
                logging.info("Found stripped file, sending response")
                flow.response = http.Response.make(
                    206,
                    d,  
                    {"Content-Length": str(len(d))}
                )
            
            else:
                logging.info("Could not determine skip, serving original file")
        
        elif flow.response.status_code == 200 and "audio" in content_type:
            logging.info(flow.response)
            logging.info("Audio file recieved")
            self.url = self.get_origin(flow.request.url)
            if not self.url:
                self.url = flow.request.url
            
            if self.url in self.stripped.keys():
                d = self.stripped[self.url]
                logging.info("Found stripped file, sending response")
            
            else:
                logging.info("Starting ad stripping...")
                data = flow.response.content
                d = self.strip_ads(data)
                if not d:
                    logging.error("Something went wrong, and the ads could not be removed. Serving original file.")
                    return
                
                self.stripped[self.url] = d
                logging.info("Ads stripped, sending response")
            
            flow.response = http.Response.make(
                200,
                d,  
                {"Content-Length": str(len(d))}
            )
        
    def strip_ads(self, data: bytes) -> bytes:
        d = b""
        prev_idx = 0
        i = 0
        try:
            with self.session.get(self.url, stream=True) as x:
                try:
                    n = int(int(x.headers["Content-Length"]) / self.delta)
                except KeyError:
                    n = "?"
                
                for chunk in x.iter_content(self.delta):
                    print(f"\rProgress: {i} / {n}", end="")
                    i += 1
                    
                    idx = data.find(chunk)
                    if idx != -1 and abs(idx-prev_idx) <= 100*self.delta:
                        d += chunk
                        prev_idx = idx
                        data = data.replace(chunk, b"", 1)
        
        except requests.exceptions.ConnectionError:
            logging.error(f"Cannot connect to the Tor SOCKS proxy. Make sure the Tor proxy is listening and the port number {self.tor_port} is correct.")
        
        print()
        return d
    
    def get_origin(self, url: str) -> str | None:
        for origin, lst in self.route.items():
            if url == origin:
                return origin
            if url in lst:
                return origin
        return None
    
    def update_route(self, req_url: str, found_url: str) -> None:
        if req_url in self.route.keys():
            if found_url not in self.route[req_url]:
                self.route[req_url].append(found_url)
        
        elif self.get_origin(req_url):
            origin = self.get_origin(req_url)
            if found_url not in self.route[origin]:
                self.route[origin].append(found_url)
        
        else:
            if len(self.route) >= 5:
                self.route = {}
                self.stripped = {}
            self.route[req_url] = [found_url]

addons = [AdStripper()]
