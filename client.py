import random
import socket
import socketserver
import threading
from time import sleep
import json
import network as nw

ip = ("192.168.1.167", 3000)


class TokenMonitor:
    def __init__(self):
        self.token = None
        self.lock = threading.Lock()

    def set_token(self, token):
        with self.lock:
            self.token = token

    def get_token(self):
        with self.lock:
            return self.token

    def clear_token(self):
        with self.lock:
            self.token = None


def think():
    print("I am thinking", end="")
    for i in range(0, random.randint(1, 20)):
        print(".", end="", flush=True)
        sleep(0.5)
    print(" No, I really do need two forks to eat!")


class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        payload = self.request[0].strip().decode()
        socket = self.request[1]

        try:
            payload = json.loads(payload)
        except json.decoder.JSONDecodeError:
            return

        if payload["token"] is not None:
            pass


class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass


tkn = TokenMonitor()


def UDPClient():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("192.168.1.167", 0))
    loc_addr = sock.getsockname()

    datagram = {
        "token": None,
        "message": "LET-ME-SIT"}

    sock.sendto(json.dumps(datagram).encode(), ip)
    # Receive response
    data, address = sock.recvfrom(1024)
    data = json.loads(data.decode())
    if data["message"] == "OK-SIT":
        nw.send_and_receive(sock, b"SIT-OK", address, 5, 0.5, None)
        print("I am sitting at the table with id %s" % data["identifier"])
        print("My token is %s" % data["token"])
        print("The next token user is %s" % data["next_token_user_address"])

    identifier = data["identifier"]
    tkn.set_token(data["token"])
    next_token_user_address = data["next_token_user_address"]
    sock.close()

    token_server = ThreadedUDPServer(loc_addr, ThreadedUDPRequestHandler)
    try:
        print(f"Accepting tokens on {loc_addr}")
        with token_server:
            server_thread = threading.Thread(target=token_server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            print(f"Server loop running in thread: {server_thread.name}")

            # Coffee machine go brrrr
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(("192.168.1.167", 0))
            while True:
                # Hunger
                print("\nI am hungry")
                # Wait for token if None
                if tkn.get_token() is None:
                    print("I am waiting for a token", end="")
                    while tkn.get_token() is None:
                        print(".", end="", flush=True)
                        sleep(2)
                else:
                    print(f"I have a token {tkn.get_token()}")
                    data = {
                        "identifier": identifier,
                        "token": tkn.get_token(),
                        "message": "HUNGRY"}
                    if nw.send_and_receive(sock, json.dumps(data).encode(), ip, 5, 3, b"OK"):
                        print("I am trying to gormandize")
                        while not nw.receive_and_send(sock, None, 600, b"GORMANDIZED"):
                            print("I have the forks and I am gormandizing")
                    else:
                        print("My token wasn't accepted")
                        continue
    except KeyboardInterrupt:
        print("Server shutting down")
        token_server.shutdown()
        token_server.server_close()


def main():
    UDPClient()


if __name__ == '__main__':
    main()
