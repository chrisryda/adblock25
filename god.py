import requests
import os.path
import os
from mitmproxy import http

os.remove("./tmp/frommitm.mp3")
os.remove("./tmp/one.mp3")

def request(flow: http.HTTPFlow) -> None:
    print(f"\nHere's the req\n{flow.request}\n")
    # if flow.request.method == "GET":
    #     Thread(target=getit, args=(flow.request.url,), daemon=True).start()

def response(flow: http.HTTPFlow) -> None:
    fname = "./tmp/one.mp3"
    if flow.response.status_code == 302 and not os.path.isfile(fname):
        with open(fname, "wb") as out:
            # print(requests.get("http://httpbin.org/ip").text)
            url = flow.request.url
            print(url)
            out.write(requests.get(flow.request.url).content)
        
    if flow.response.status_code == 200:
        with open("./tmp/frommitm.mp3", "wb") as out:
            out.write(flow.response.content)
    
#     data = flow.response.content
#     d = b""
#     with requests.get(flow.request.url, stream=True) as x:
#         for chunk in x.iter_content(2048):
#             if data.find(chunk) >= 0:
#                 d += chunk
#     flow.response.data.content = d
    # with open("./tmp/onebeer.mp3", "rb") as x:
    #     gad = x.read()
    # flow.response = http.Response.make(
    #     200,
    #     gad,  
    #     {"Content-Length": str(len(gad))}
    # )
    



