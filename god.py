import requests
import os.path
import os
from mitmproxy import http

def refresh():
    try:
        os.remove("./tmp/frommitm.mp3")
        os.remove("./tmp/one.mp3")
        os.remove("./tmp/response.mp3")
    except FileNotFoundError:
        pass
    
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

class MitmAddon:
    def __init__(self):
        self.delta = 2**14 # 2**11 = 2048
        self.num = 0
        self.url = ""
        self.d = b""
        self.accessed = False
        refresh()
    
    def response(self, flow: http.HTTPFlow) -> None:
        self.num += 1
        flow.response.headers["count"] = str(self.num)
        if flow.response.status_code == 302 and self.num == 1:
            self.url = flow.request.url
        
        if self.url and flow.response.status_code == 200:
            if not self.accessed:
                self.accessed = True
                data = flow.response.content
                with requests.get(self.url, stream=True) as x:
                    with open("./tmp/one.mp3", "wb") as out: # DEL
                        for chunk in x.iter_content(self.delta):
                            out.write(chunk) # DEL
                            if data.find(chunk) != -1:   
                                self.d += chunk
            # print("Writing content")
            with open("./tmp/frommitm.mp3", "wb") as out:
                out.write(flow.response.content)
            
            with open("./tmp/response.mp3", "wb") as out:
                out.write(self.d)
            
            flow.response = http.Response.make(
                200,
                self.d,  
                {"Content-Length": str(len(self.d))}
            )

addons = [MitmAddon()]
