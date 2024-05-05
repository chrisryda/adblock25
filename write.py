import os
import shutil
import requests
from mitmproxy import http

class AdStripper:
    def __init__(self):
        self.refresh()
        self.delta = 2**13
        self.url = ""
        self.route = {}
        self.stripped = {}
        os.mkdir("./tmp")
    
    def response(self, flow: http.HTTPFlow) -> None:
        if flow.response.status_code == 302:
            self.update_route(flow.request.url, flow.response.headers["location"])
            return
        
        try:
            content_type = flow.response.headers["Content-Type"]
        except KeyError:
            return
        
        if flow.response.status_code == 200 and content_type == "audio/mpeg":
            try:
                client_id = flow.client_conn.id
                os.mkdir(f"./tmp/{client_id}")
            except FileExistsError:
                pass
            
            if self.url in self.stripped.keys():
                d = self.stripped[self.url]
                print("Found stripped file, sending response")
            else:
                data = flow.response.content
                d = self.strip_ads(data, flow.client_conn.id)
                self.stripped[self.url] = d
                print("Ads stripped, sending response")
            
            self.write(flow, d, client_id)
                
            flow.response = http.Response.make(
                200,
                d,  
                {"Content-Length": str(len(d))}
            )
        
    def strip_ads(self, data: bytes, client_id) -> bytes:
        d = b""
        print(self.url)
        session = self.get_tor_session()
        with session.get(self.url, stream=True) as x:
            with open(f"./tmp/{client_id}/one.mp3", "wb") as out:
                for chunk in x.iter_content(self.delta):
                    out.write(chunk)
                    if data.find(chunk) != -1:   
                        d += chunk
        return d
    
        
    def get_tor_session(self):
        session = requests.session()
        session.proxies = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}
        return session

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
            self.route = {}
            self.stripped = {}
            self.url = req_url
            self.route[req_url] = [found_url]

    def write(self, flow: http.HTTPFlow, d: bytes, client_id):
        with open(f"./tmp/{client_id}/frommitm.mp3", "wb") as out:
            out.write(flow.response.content)
        with open(f"./tmp/{client_id}/response.mp3", "wb") as out:
            out.write(d)
    
    def refresh(self):
        try:
            shutil.rmtree("./tmp")
        except FileNotFoundError:
            pass
        
addons = [AdStripper()]
