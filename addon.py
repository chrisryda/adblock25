import requests
from mitmproxy import http

class AdStripper:
    def __init__(self):
        self.delta = 2**13
        self.url = ""
        self.route = {}
        self.stripped = {}
    
    def response(self, flow: http.HTTPFlow) -> None:
        if flow.response.status_code == 302:
            self.update_route(flow.request.url, flow.response.headers["location"])
            return
        
        try:
            content_type = flow.response.headers["Content-Type"]
        except KeyError:
            return
        
        if flow.response.status_code == 200 and content_type == "audio/mpeg":
            if self.url in self.stripped.keys():
                d = self.stripped[self.url]
            else:
                data = flow.response.content
                d = self.strip_ads(data)
                self.stripped[self.url] = d
        
            print("Ads stripped, sending response")
            flow.response = http.Response.make(
                200,
                d,  
                {"Content-Length": str(len(d))}
            )
        
    def strip_ads(self, data: bytes) -> bytes:
        d = b""
        with requests.get(self.url, stream=True) as x:
            for chunk in x.iter_content(self.delta):
                if data.find(chunk) != -1:   
                    d += chunk
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
            self.route = {}
            self.stripped = {}
            self.url = req_url
            self.route[req_url] = [found_url]

addons = [AdStripper()]
