import requests
import os.path
import os
from mitmproxy import http

# Se på connections mot en host: f.eks megaphone.fm, og sende samme d til alle
# Forbedre if-statement linje 27    

def refresh():
    try:
        os.remove("./tmp/frommitm.mp3")
        os.remove("./tmp/one.mp3")
        os.remove("./tmp/response.mp3")
    except FileNotFoundError:
        pass
    
class AdStripper:
    def __init__(self):
        self.delta = 2**14 # 2**11 = 2048
        self.url = ""
        self.accessed = False 
        self.connections = {}
        refresh()
    
    def response(self, flow: http.HTTPFlow) -> None:
        try:
            content_type = flow.response.headers["Content-Type"]
        except KeyError:
            return
        
        if content_type != "audio/mpeg":
            if flow.response.status_code == 302 and not self.accessed:
                self.accessed = True
                self.url = flow.request.url
        
        else:
            if flow.response.status_code == 200 and self.url:
                data = flow.response.content
                print("Going in")
                self.d = self.strip_ads(data)
                print("Ads stripped, sending response")
                flow.response = http.Response.make(
                    200,
                    self.d,  
                    {"Content-Length": str(len(d))}
                )
                
                # with open("./tmp/frommitm.mp3", "wb") as out:
                #     out.write(flow.response.content)
                # with open("./tmp/response.mp3", "wb") as out:
                #     out.write(d)
                self.accessed = False
        
        
    def strip_ads(self, data: bytes) -> bytes:
        d = b""
        with requests.get(self.url, stream=True) as x:
            # with open("./tmp/one.mp3", "wb") as out: # DEL
            for chunk in x.iter_content(self.delta):
                # out.write(chunk) # DEL
                if data.find(chunk) != -1:   
                    d += chunk
        return d

addons = [AdStripper()]
