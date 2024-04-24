from threading import Thread
import requests
import socket
import sys

class Proxy:
    def __init__(self, port=3000):
        self.port = port
        self.proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.proxy.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.buffer_size = 2048

    def run(self):
        # ip = input("Enter IP-address of the Waydroid-instance: ")
        # self.proxy.bind(("ip", self.port))
        self.proxy.bind(("192.168.240.1", self.port)) # What's up with needing this specific IP? 192.168.240.x
        self.proxy.listen(100)
        print("  * Proxy server is running on port {}".format(self.port))
        
        while True:
            try:
                client, addr = self.proxy.accept()
                req = client.recv(self.buffer_size)
                head = self.parse_req(req)
                
                print(f"\nRequest recieved => {addr[0]}:{addr[1]}")
                print(head)
                Thread(target=self.handle_request, args=(client, req, head), daemon=True).start()
            except KeyboardInterrupt:
                print("\n\nCtrl+C pressed, exiting...")
                sys.exit(0)

    def handle_request(self, client : socket, req : bytes, head : dict) -> None:
        print("Handling req")
        hp = head["headers"]["host"].split(":")
        host = hp[0]
        try:
            port = int(hp[1])
        except IndexError:
            port = 80
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((socket.gethostbyname(host), port))
        
        if head["method"] == "CONNECT":
            self.serve_tunnel(client, server)
        
        else:
            server.sendall(req)
            res = server.recv(self.buffer_size)
            client.sendall(res)
            
            head = self.parse_req(res)
            headers = head["headers"]
            data = head["chunk"]
            if "content-length" in headers:
                n = int(headers["content-length"]) - len(data)
                while n > 0:
                    s = server.recv(n)
                    if not s: break
                    client.sendall(s)
                    res += s
                    n -= len(s)   
            print("Response sent")
            
        server.close()
        client.close()
        return
    
    def serve_tunnel(self, client : socket, server : socket) -> None:
        reply = "HTTP/1.0 200 HTTP/1.0 200 Connection established\r\n\r\n"
        client.sendall(reply.encode())  
        server.setblocking(0)
        client.setblocking(0)
        print("Serving tunnel")
        i = 0
        while True:
            try:
                res = server.recv(self.buffer_size)
                client.sendall(res)
                i = 0
            except socket.error as err:
                i += 1
            try:
                req = client.recv(self.buffer_size)
                server.sendall(req)
                i = 0
            except socket.error as err:
                i += 1
            
            if i > 100_000:            
                print("Empty tunnel, quitting")
                break
    
    
    def parse_req(self, req : bytes) -> dict:
        nodes = req.split(b"\r\n\r\n")
        heads = nodes[0].split(b"\r\n")
        meta = heads.pop(0).decode("utf-8")
        data = {
            "method" : meta.split(" ")[0],
            "meta": meta,
            "headers": {},
            "chunk": b""
        }
        if len(nodes) >= 2:
            data["chunk"] = nodes[1]
    
        for head in heads:
            pieces = head.split(b": ")
            key = pieces.pop(0).decode("utf-8")
            if key.startswith("Connection: "):
                data["headers"][key.lower()] = "keep-alive"
            else:
                data["headers"][key.lower()] = b": ".join(pieces).decode("utf-8")
        return data

if __name__ == "__main__":
    proxy = Proxy(3001)
    proxy.run()
