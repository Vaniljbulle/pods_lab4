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

NAPPING_RATE_DEFAULT = .1
NAPPING_RATE_INCREMENT = .05
SEND_RATE = .99

napping_rate = NAPPING_RATE_DEFAULT
napping_rate_permanent = .1
napping = False


def napper():
    global napping_rate
    global napping
    print("Napper running")
    while True:
        if random.random() <= napping_rate:
            napping_rate = NAPPING_RATE_DEFAULT
            print("Nvm, I am going to sleep for ", end="")
            napping = True
            if random.random() <= napping_rate_permanent:
                print("forever. Bye!")
                break
            else:
                i = random.randint(5, 20)
                print(f"{i} seconds")
                sleep(i)
                napping = False
        napping_rate += NAPPING_RATE_INCREMENT
        sleep(5)


def send_chance():
    return random.random() <= SEND_RATE


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

        if not napping:
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
        c = 0
        while c < 10:
            if not napping:
                if send_chance():
                    s.sendto(json.dumps(message).encode(), next_user.get())
                else:
                    print("SIMULATED ERROR: Sent token into the void")
                try:
                    c += 1
                    data = s.recv(100)
                    if data == b"token-accepted":
                        return
                except socket.timeout:
                    pass  # try again
                except Exception as e:
                    break

    # Assumed dead, send token to server
    print("Target assumed dead, returning token to server")
    transport = TSocket.TSocket(ip_server[0], ip_server[1])
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = tableService.Client(protocol)
    transport.open()

    while True:
        if not napping and send_chance():
            # data = [message, ip, port, token, identifier, next_token_ip, next_token_port]
            request = ["RETURN-TOKEN", "None", "None", tkn, identifier.get(), "None", "None"]
            answer = client.return_token(request)
            if answer[0] == "OK-NEW-NEXT":
                print("New next user set to", answer[5], answer[6])
                next_user.set((answer[5], int(answer[6])))
                break
            elif answer[0] == "ERROR-UNSEATED":
                print("ERROR: I am not seated")
                raise Exception("I am not seated")
            elif answer[0] == "ERROR-INVALID-TOKEN":
                break  # Was already deleted
        else:
            print("SIMULATED ERROR: I am not sending the request")

    transport.close()


class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass


def think():
    print("I am thinking")
    for i in range(0, random.randint(1, 20)):
        sleep(0.5)
    print("I am done thinking")


# data = [message, ip, port, token, identifier, next_token_ip, next_token_port]
def client_loop(client, port):
    while True:
        print(f"Seat requested")
        request = ["LET-ME-SIT", ip_me[0], str(port), "None", "None", "None", "None"]
        answer = ["ERROR", "None", "None", "None", "None", "None", "None"]
        if not napping and send_chance():
            answer = client.take_seat(request)
        else:
            print("SIMULATED ERROR: I am not sending the request")
        if answer[0] == "OK-SEATED":
            print("Seat granted")
            # print(f"Token: {answer[3]}")
            token.set(answer[3])
            # print(f"Identifier: {answer[4]}")
            identifier.set(answer[4])
            # print(f"Next user: {answer[5]}:{answer[6]}")
            next_user.set((answer[5], int(answer[6])))
            break
        elif answer[0] == "ERROR":
            print("Server did not respond.. I will try again in a few seconds")
        elif answer[0] == "ERROR-ALREADY-SEATED":
            print("I am already seated")
            break
        sleep(5)

    while True:
        print(f"\nI am gormandizing")
        if token.get() is None or token.get() == "None":
            print("I am waiting for a token", end="")
            while token.get() is None or token.get() == "None":
                print(".", end="", flush=True)
                sleep(2)
            print(" Token received")
        request = ["I-AM-HUNGRY", ip_me[0], str(port), token.get(), identifier.get(), "None", "None"]
        answer = ["ERROR", "None", "None", "None", "None", "None", "None"]
        if not napping and send_chance():
            answer = client.hunger(request)
        else:
            print("SIMULATED ERROR: I am not sending the request")
        if answer[0] == "GORMANDIZED":
            print("I am done gormandizing")
        elif answer[0] == "ERROR-UNSEATED":
            print("I was unseated")
            raise Exception("UNSEATED")
        elif answer[0] == "ERROR-TOKEN-REVOKED":
            print("My token was revoked")
            token.clear()
            continue
        else:
            print("I was ignored.. I will try again in a few seconds")
            sleep(3)
            continue
        pass_token(token.replace("None"))
        think()


def main():
    #nap = threading.Thread(target=napper)
    #nap.start()

    print("Starting token server")
    server_token = ThreadedUDPServer(ip_me, ThreadedUDPRequestHandler)
    server_thread = threading.Thread(target=server_token.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # get port from server_token
    port = server_token.server_address[1]
    print(f"port = {port}")
    print(f"Server loop running in thread: {server_thread.name}")
    transport = TSocket.TSocket(ip_server[0], ip_server[1])
    while True:
        try:
            transport = TSocket.TSocket(ip_server[0], ip_server[1])
            transport = TTransport.TBufferedTransport(transport)
            protocol = TBinaryProtocol.TBinaryProtocol(transport)
            client = tableService.Client(protocol)

            transport.open()
            client_loop(client, port)
        except KeyboardInterrupt:
            server_thread.join()
            #nap.join()
            break
        except Exception as e:
            print(f"\nServer is offline. Trying again in 10 seconds.")
            sleep(3)
            transport.close()

    print("Closing connection")
    transport.close()


if __name__ == "__main__":
    main()
