import socket
import sys
from threading import Thread, main_thread

class Proxy:
    def __init__(self, port=3000):
        self.port = port
        self.proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.proxy.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.buffer_size = 4096

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
                head = self.parse_head(req)
                
                print(f"\nRequest recieved => {addr[0]}:{addr[1]}")
                print(head)
                workers = []
                if head["method"] == "CONNECT":
                    t = Thread(target=self.serve_tunnel, args=(client, head), daemon=True)
                    t.start()
                    workers.append(t)
                else:
                    t = Thread(target=self.handle_request, args=(client, req, head), daemon=True)
                    t.start()
                    workers.append(t)
            except KeyboardInterrupt:
                print("\n\nCtrl+C pressed, exiting...")
                for t in workers:
                    t.join()
                sys.exit(0)

    def handle_request(self, client, req, head):
        port = 80
        print("Handling req")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((socket.gethostbyname(head["headers"]["host"].split(":")[0]), port))
        server.sendall(req)
        print("Waiting for response...")
        res = server.recv(self.buffer_size)
        client.sendall(res)
        print(f"Response recieved")
        head = self.parse_head(res)
        headers = head["headers"]
        server.setblocking(0)
        client.setblocking(0)
        while True:
            try:
                request = server.recv(self.buffer_size)
                # print(f"Request:\n{request}")
                client.sendall( request )
            except socket.error as err:
                # print(err)
                pass
            try:
                reply = client.recv(self.buffer_size)
                # print(f"Reply:\n{reply}")
                server.sendall( reply )
            except socket.error as err:
                # print(err)
                pass
            except KeyboardInterrupt:
                return

    #def send_to_server(self, host, port, data):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((socket.gethostbyname(host.split(":")[0]), port))
        server.sendall(data)
        print("Waiting for response...")
        res = server.recv(self.buffer_size)
        print(f"Response recieved")
        head = self.parse_head(res)
        headers = head["headers"]
        
        if "content-length" in headers and int(headers["content-length"]) > self.buffer_size:
            n = (int(headers["content-length"]) / self.buffer_size)
            if n > 2: 
                res += server.recv(int(headers["content-length"]))
                print("Gathering data")
            res += server.recv(int(self.buffer_size*(n - int(n)))+1)
        
        # print(res)
        server.close()
        return res

    def serve_tunnel(self, client, head):
        host = head["headers"]["host"].split(":")[0]
        port = int(head["headers"]["host"].split(":")[1])
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((socket.gethostbyname(host), port))
        if head["method"] == "CONNECT":
            try:
                reply = "HTTP/1.0 200 HTTP/1.0 200 Connection established\r\n\r\n"
                # print(reply)
                client.sendall(reply.encode())
            except socket.error as err:
                # If the connection could not be established, exit
                # Should properly handle the exit with http error code here
                print(err)  
            server.setblocking(0)
            client.setblocking(0)
            print("Serving tunnel")
            while True:
                try:
                    request = server.recv(self.buffer_size)
                    # print(f"Request:\n{request}")
                    client.sendall( request )
                except socket.error as err:
                    # print(err)
                    pass
                try:
                    reply = client.recv(self.buffer_size)
                    # print(f"Reply:\n{reply}")
                    server.sendall( reply )
                except socket.error as err:
                    # print(err)
                    pass
                except KeyboardInterrupt:
                        return

    # def recvall(self, c, n):
    #     data = b''
    #     while n > 0:
    #         s = c.recv(n)
    #         if not s: raise EOFError
    #         data += s
    #         n -= len(s)
    #     return data
    
    def parse_head(self, head_request):
        nodes = head_request.split(b"\r\n\r\n")
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
