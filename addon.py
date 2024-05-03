import requests
from mitmproxy import http

class AdStripper:
    def __init__(self):
        self.delta = 2**13
        self.url = ""
        self.num = 0
        self.route = {}
        self.stripped = {}
    
    def request(self, flow: http.HTTPFlow) -> None:
        self.num += 1
        flow.request.headers["count"] = str(self.num)
        if self.num == 1:
            self.route[flow.request.url] = []
    
    def response(self, flow: http.HTTPFlow) -> None:
        if flow.response.status_code == 302:
            req_url = flow.request.url
            found_url = flow.response.headers["location"]
            
            if req_url in self.route.keys():
                print(f"Key {req_url} already exists")
                if found_url not in self.route[req_url]:
                    self.route[req_url].append(found_url)
            
            elif self.innit(req_url):
                origin = self.get_origin(req_url)
                if found_url not in self.route[origin]:
                    self.route[origin].append(found_url)
            
            else:
                self.route[req_url] = [found_url]

            print(f"Num of keys: {len(list(self.route.keys()))}")
            print(self.route)
            self.url = flow.request.url
            return
        
        try:
            content_type = flow.response.headers["Content-Type"]
        except KeyError:
            content_type = ""
            pass
        
        if flow.response.status_code == 200 and content_type == "audio/mpeg":
            if not self.url:
                self.url = flow.request.url
            data = flow.response.content
            d = self.strip_ads(data)
            print("Ads stripped, sending response")
            flow.response = http.Response.make(
                200,
                d,  
                {"Content-Length": str(len(d))}
            )
        
        else:
            return
        
    def strip_ads(self, data: bytes) -> bytes:
        d = b""
        with requests.get(self.url, stream=True) as x:
            for chunk in x.iter_content(self.delta):
                if data.find(chunk) != -1:   
                    d += chunk
        return d

    def innit(self, req_url: str) -> bool:
        for lst in self.route.values():
            if req_url in lst:
                return True
        return False
    
    def get_origin(self, url: str) -> str | None:
        for origin, lst in self.route.items():
            if url in lst:
                return origin
        return None

addons = [AdStripper()]
