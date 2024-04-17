import socket
from threading import Thread


class Proxy:
    def __init__(self, port=3000):
        self.port = port
        self.proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.buffer_size = 4096

    def run(self):
        self.proxy.bind(("0.0.0.0", self.port))
        self.proxy.listen(100)
        print("  * Proxy server is running on port {}".format(self.port))

        while True:
            client, addr = self.proxy.accept()
            print("\nRequest recieved => {}:{}".format(addr[0], addr[1]))
            Thread(target=self.handle_request, args=(client,)).start()

    def handle_request(self, client):
        req = client.recv(self.buffer_size)
        head = self.parse_head(req)
        # print(head)
        port = 80
        response = self.send_to_server(head["headers"]["host"], port, req)
        client.sendall(response)
        print(response)
        client.close()

    def send_to_server(self, host, port, data):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((socket.gethostbyname(host), port))
        server.sendall(data)
        res = server.recv(self.buffer_size)
        head = self.parse_head(res)
        headers = head["headers"]
        if "content-length" in headers:
            prev = b""
            while len(res) != len(prev):
                prev = res
                res += server.recv(self.buffer_size)

        print(f"\nResonse len {len(res)}")
        server.close()
        return res

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
                data["headers"][key.lower()] = "close"
            else:
                data["headers"][key.lower()] = b": ".join(pieces).decode("utf-8")
        return data

if __name__ == "__main__":
    proxy = Proxy(3001)
    proxy.run()
