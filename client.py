import json
import random
import socket
import socketserver
import threading
from time import sleep

import monitors
from tblService import tableService
from tblService.ttypes import *

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

# data = [message, ip, port, token, identifier, next_token_ip, next_token_port]

ip_server = ('192.168.1.167', 3000)
ip_me = ("192.168.1.167", 0)

token = monitors.ThreadSafeVariable()
next_user = monitors.ThreadSafeVariable()
identifier = monitors.ThreadSafeVariable()


class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        payload = self.request[0].strip().decode()
        socket = self.request[1]

        try:
            payload = json.loads(payload)
        except json.decoder.JSONDecodeError:
            return
        if payload['message'] == 'new-token':
            tkn = token.get()
            socket.sendto("token-accepted".encode(), self.client_address)
            if tkn == payload['token']:
                return
            elif tkn == "None" or tkn is None:
                token.set(payload['token'])
            else:
                old_token = token.replace(payload['token'])
                pass_token(old_token)
        elif payload['message'] == 'new-next-user':

            next_user.set((payload['ip'], int(payload['port'])))
            socket.sendto("next-user-accepted".encode(), self.client_address)
            print("Next user set to", next_user.get())


def pass_token(tkn):
    if next_user.get()[0] == ip_me:
        return
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(3)
        message = {"message": "new-token", "token": tkn}
        while True:
            s.sendto(json.dumps(message).encode(), next_user.get())
            try:
                data = s.recv(100)
                if data == b"token-accepted":
                    return
            except socket.timeout:
                pass  # try again


class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass


def think():
    print("I am thinking", end="")
    for i in range(0, random.randint(1, 20)):
        print(".", end="", flush=True)
        sleep(0.5)
    print(" No, I really do need two forks to eat!")


# data = [message, ip, port, token, identifier, next_token_ip, next_token_port]
def client_loop(client, port):
    while True:
        print(f"Seat requested")
        request = ["LET-ME-SIT", ip_me[0], str(port), "None", "None", "None", "None"]
        answer = client.take_seat(request)
        if answer[0] == "OK-SEATED":
            print("Seat granted")
            print(f"Token: {answer[3]}")
            token.set(answer[3])
            print(f"Identifier: {answer[4]}")
            identifier.set(answer[4])
            print(f"Next user: {answer[5]}:{answer[6]}")
            next_user.set((answer[5], int(answer[6])))
            break
        sleep(3)

    while True:
        print(f"\nI am hungry")
        if token.get() is None or token.get() == "None":
            print("I am waiting for a token", end="")
            while token.get() is None or token.get() == "None":
                print(".", end="", flush=True)
                sleep(2)
        request = ["I-AM-HUNGRY", ip_me[0], str(port), token.get(), identifier.get(), "None", "None"]
        answer = client.hunger(request)
        if answer[0] == "GORMANDIZED":
            print("I am done gormandizing")
        else:
            print("I didnt get to it. I wasnt hungry anyway.")
        pass_token(token.replace("None"))
        think()


def main():
    print("Starting token server")
    server_token = ThreadedUDPServer(ip_me, ThreadedUDPRequestHandler)
    server_thread = threading.Thread(target=server_token.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # get port from server_token
    port = server_token.server_address[1]
    print(f"port = {port}")
    print(f"Server loop running in thread: {server_thread.name}")

    print("Starting client")
    transport = TSocket.TSocket(ip_server[0], ip_server[1])
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = tableService.Client(protocol)

    transport.open()
    print("Client started")

    try:
        client_loop(client, port)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)

    print("Closing connection")

    transport.close()


if __name__ == "__main__":
    main()
