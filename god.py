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
        self.accessed = False
        refresh()
    
    # def request(self, flow: http.HTTPFlow) -> None:
    
    def response(self, flow: http.HTTPFlow) -> None:
        self.num += 1
        flow.response.headers["count"] = str(self.num)
        if flow.response.status_code == 302 and self.num == 1:
            self.url = flow.request.url
            print(self.url)
            # with open("./tmp/one.mp3", "wb") as out:
            #     out.write(requests.get(self.url).content)    
        
        if self.url and flow.response.status_code == 200 and not self.accessed:
            self.accessed = True
            d = b""
            # data = list(chunks(flow.response.content, self.delta))
            data = flow.response.content
            with requests.get(self.url, stream=True) as x:
                with open("./tmp/one.mp3", "wb") as out: # DEL
                    for chunk in x.iter_content(self.delta):
                        out.write(chunk) # DEL
                        if data.find(chunk) != -1:   
                            d += chunk
            
            # print("Writing content")
            with open("./tmp/frommitm.mp3", "wb") as out:
                out.write(flow.response.content)
            
            with open("./tmp/response.mp3", "wb") as out:
                out.write(d)
            
            # flow.response = http.Response.make(
            #     200,
            #     d,  
            #     {"Content-Length": str(len(d))}
            # )

addons = [MitmAddon()]
