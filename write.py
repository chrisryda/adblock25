import os
import shutil
import requests
from mitmproxy import http

class AdStripper:
    def __init__(self):
        self.refresh()
        self.delta = 2**13
        self.url = ""
        os.mkdir("./tmp")

    def response(self, flow: http.HTTPFlow) -> None:
        if flow.response.status_code == 302:
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
            
            try:
                client_id = flow.client_conn.id
                os.mkdir(f"./tmp/{client_id}")
            except FileExistsError:
                pass
            
            d = self.strip_ads(data, client_id)
            print("Ads stripped, sending response")
            flow.response = http.Response.make(
                200,
                d,  
                {"Content-Length": str(len(d))}
            )
            
            with open(f"./tmp/{client_id}/frommitm.mp3", "wb") as out:
                out.write(flow.response.content)
            with open(f"./tmp/{client_id}/response.mp3", "wb") as out:
                out.write(d)
        
        else:
            return
        
    def strip_ads(self, data: bytes, client_id) -> bytes:
        d = b""
        with requests.get(self.url, stream=True) as x:
            with open(f"./tmp/{client_id}/one.mp3", "wb") as out:
                for chunk in x.iter_content(self.delta):
                    out.write(chunk)
                    if data.find(chunk) != -1:   
                        d += chunk
        return d
    
    def refresh(self):
        try:
            shutil.rmtree("./tmp")
        except FileNotFoundError:
            pass
        
addons = [AdStripper()]
