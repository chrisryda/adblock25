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
        self.connections = []
        refresh()
    
    def response(self, flow: http.HTTPFlow) -> None:
        try:
            if flow.response.headers["Content-Type"] != "audio/mpeg":
                if (flow.response.status_code == 302 and flow.client_conn not in self.connections):
                    self.url = flow.request.url
                    self.connections.append(flow.client_conn)
                return
        
        except KeyError:
                return
        
        if flow.response.status_code == 200 and self.url :
            print(f"Going for it with url: {self.url}")
            data = flow.response.content
            d = self.strip_ads(data)
            print("Ads stripped, sending response")
            flow.response = http.Response.make(
                200,
                d,  
                {"Content-Length": str(len(d))}
            )
            with open("./tmp/frommitm.mp3", "wb") as out:
                out.write(flow.response.content)
            with open("./tmp/response.mp3", "wb") as out:
                out.write(d)


    def strip_ads(self, data: bytes) -> bytes:
        d = b""
        with requests.get(self.url, stream=True) as x:
            with open("./tmp/one.mp3", "wb") as out: # DEL
                for chunk in x.iter_content(self.delta):
                    out.write(chunk) # DEL
                    if data.find(chunk) != -1:   
                        d += chunk
        return d

addons = [AdStripper()]
