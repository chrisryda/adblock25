import requests
from mitmproxy import http

class AdStripper:
    def __init__(self):
        self.delta = 2**13
        self.url = ""
    
    def response(self, flow: http.HTTPFlow) -> None:
        if flow.response.status_code == 302:
            self.url = flow.request.url
            return
        
        try:
            content_type = flow.response.headers["Content-Type"]
        except KeyError:
            content_type = ""
            pass
        
        if flow.response.status_code == 200 and content_type == "audio/mpeg" and self.url:
            data = flow.response.content
            print("Going in")
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

addons = [AdStripper()]
