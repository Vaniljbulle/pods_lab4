import random
import socket
import socketserver
import threading
from time import sleep
import json
import network as nw

ip = ("192.168.1.167", 3000)


class Monitor:
    def __init__(self):
        self.value = None
        self.lock = threading.Lock()

    def set(self, new_value):
        with self.lock:
            self.value = new_value

    def get(self):
        with self.lock:
            return self.value

    def clear(self):
        with self.lock:
            self.value = None

    def replace(self, new_value):
        with self.lock:
            old_value = self.value
            self.value = new_value
            return old_value

    def is_set(self):
        with self.lock:
            return self.value is not None


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

        if payload["message"] == "new-token":
            if token.get() is None:
                token.set(payload["token"])
                socket.sendto(b"TOKEN-OK", self.client_address)
            else:
                old_token = token.replace(payload["token"])
                pass_token(old_token, socket)
        elif payload["message"] == "new-next-user":
            next_token_user_address.set(payload["next_token_user_address"])
            socket.sendto("NEXT-USER-OK".encode(), self.client_address)


def pass_token(old_token, socket_s):
    nt = next_token_user_address.get()
    if nw.send_and_receive(socket_s, json.dumps({"token": old_token, "message": "new-token"}).encode(), (nt[0], nt[1]),
                           5, 2,
                           b"TOKEN-OK"):
        print("Token passed to next user.")
    else:
        print("Next user in ring did not accept token.")
        print("Returning token to server.")
        sleep(5)


class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass


token = Monitor()
next_token_user_address = Monitor()


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
        print("\nI am sitting at the table with id %s" % data["identifier"])
        print("My token is %s" % data["token"])
        print("The next token user is %s" % data["next_token_user_address"])

    identifier = data["identifier"]
    token.set(data["token"])
    next_token_user_address.set(data["next_token_user_address"])

    sock.close()

    token_server = ThreadedUDPServer(loc_addr, ThreadedUDPRequestHandler)
    try:
        with token_server:
            server_thread = threading.Thread(target=token_server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            print(f"Accepting tokens on {loc_addr}")
            print(f"Server loop running in thread: {server_thread.name}")

            # Coffee machine go brrrr
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(("192.168.1.167", 0))
            while True:
                # Hunger
                print("\nI am hungry")
                # Wait for token if None
                if token.get() is None:
                    print("I am waiting for a token", end="")
                    while token.get() is None:
                        print(".", end="", flush=True)
                        sleep(2)

                print(f"I have a token {token.get()}")
                data = {
                    "identifier": identifier,
                    "token": token.get(),
                    "message": "HUNGRY"}
                if nw.send_and_receive(sock, json.dumps(data).encode(), ip, 5, 3, b"OK"):
                    print("I am trying to gormandize")
                    while not nw.receive_and_send(sock, None, 600, b"GORMANDIZED"):
                        print("I am still waiting for forks")
                    if next_token_user_address.get()[1] != loc_addr[1]:
                        pass_token(token.replace(None), sock)
                else:
                    # TODO: Clear token?
                    print("My token wasn't accepted")
                    continue
                # Think
                think()

    except KeyboardInterrupt:
        print("Server shutting down")
        token_server.shutdown()
        token_server.server_close()


def main():
    UDPClient()


if __name__ == '__main__':
    main()
