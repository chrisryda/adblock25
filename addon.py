import requests
from mitmproxy import http

class AdStripper:
    def __init__(self):
        self.session = self.get_tor_session()
        self.delta = 2**13
        self.url = ""
        self.route = {}
        self.stripped = {}
    
    def get_tor_session(self):
        session = requests.session()
        session.proxies = {'http': 'socks5://127.0.0.1:9050', 'https': 'socks5://127.0.0.1:9050'}
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
            print(flow.response)
            if self.url in self.stripped.keys():
                d = self.stripped[self.url]
                print("Found stripped file, sending response")
            else:
                data = flow.response.content
                d = self.strip_ads(data)
                self.stripped[self.url] = d
                print("\nAds stripped, sending response")
            
            flow.response = http.Response.make(
                200,
                d,  
                {"Content-Length": str(len(d))}
            )
        
    def strip_ads(self, data: bytes) -> bytes:
        d = b""
        prev_idx = 0
        i = 0
        with self.session.get(self.url, stream=True) as x:
            n = int(int(x.headers["Content-Length"]) / self.delta)
            for chunk in x.iter_content(self.delta):
                i += 1
                print(f"\rProgress: {i} / {n}", end="")
                idx = data.find(chunk)
                if idx != -1 and abs(idx-prev_idx) <= 100*self.delta :   
                    d += chunk
                prev_idx = idx
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

addons = [AdStripper()]
