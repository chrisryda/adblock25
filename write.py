import os
import shutil
import requests
from mitmproxy import http
import logging

class AdStripper:
    def __init__(self):
        self.session = self.get_tor_session()
        self.delta = 2**13
        self.url = ""
        self.route = {}
        self.stripped = {}
        self.refresh()
        os.mkdir("./tmp")
    
    def get_tor_session(self):
        session = requests.session()
        session.proxies = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}
        return session
    
    def response(self, flow: http.HTTPFlow) -> None:
        if flow.response.status_code == 302:
            self.update_route(flow.request.url, flow.response.headers["location"])
            return
        
        try:
            content_type = flow.response.headers["Content-Type"]
        except KeyError:
            return
        
        if flow.response.status_code == 200 and content_type == "audio/mpeg": 
            logging.info(flow.response)
            if self.url in self.stripped.keys():
                d = self.stripped[self.url]
                logging.info("Found stripped file, sending response")
            else:
                data = flow.response.content
                d = self.strip_ads(data, flow)
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
        
    def strip_ads(self, data: bytes, flow: http.HTTPFlow) -> bytes:
        try:
            client_id = flow.client_conn.id
            os.mkdir(f"./tmp/{client_id}")
        except FileExistsError:
            pass
        
        d = b""
        prev_idx = 0
        i = 0
        with self.session.get(self.url, stream=True) as x:
            with open(f"./tmp/{client_id}/tor.mp3", "wb") as out, open(f"./tmp/{client_id}/removed.mp3", "wb") as rem:
                try:
                    n = int(int(x.headers["Content-Length"]) / self.delta)
                except KeyError:
                    n = "?"
                
                for chunk in x.iter_content(self.delta):
                    out.write(chunk)
                    print(f"\rProgress: {i} / {n}", end="")
                    i += 1
                    
                    idx = data.find(chunk)
                    if idx != -1 and abs(idx-prev_idx) <= 100*self.delta :   
                        d += chunk
                        data = data.replace(chunk, b"", 1)
                    else:
                        rem.write(chunk)
                    prev_idx = idx
        self.write(flow, d, client_id)
        print()
        return d
    
    def route_contains(self, req_url: str) -> bool:
        for lst in self.route.values():
            if req_url in lst:
                return True
        return False
    
    def get_origin(self, url: str) -> str | None:
        for origin, lst in self.route.items():
            if url in lst:
                return origin
        return None
    
    def update_route(self, req_url: str, found_url: str) -> None:
        if req_url in self.route.keys():
            if found_url not in self.route[req_url]:
                self.route[req_url].append(found_url)
        
        elif self.route_contains(req_url):
            origin = self.get_origin(req_url)
            if found_url not in self.route[origin]:
                self.route[origin].append(found_url)
        
        else:
            if len(self.route) >= 5:
                self.route = {}
                self.stripped = {}
            self.url = req_url
            self.route[req_url] = [found_url]
    
    def write(self, flow: http.HTTPFlow, d: bytes, client_id):
        with open(f"./tmp/{client_id}/mitm.mp3", "wb") as out:
            out.write(flow.response.content)
        with open(f"./tmp/{client_id}/response.mp3", "wb") as out:
            out.write(d)
    
    def refresh(self):
        try:
            shutil.rmtree("./tmp")
        except FileNotFoundError:
            pass

addons = [AdStripper()]
