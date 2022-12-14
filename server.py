import json
import random
import socket
import socketserver
import string
import threading
import typing
import os
import monitors

from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket
from thrift.transport import TTransport
import table
from tblService import tableService

ip_server = ("192.168.1.167", 3000)
ip_me = ("192.168.1.167", 0)
tbl = table.Table()
tokens = monitors.ThreadSafeList()


def generate_token():
    if tbl.philosophers.__len__() != 1:
        token = generate_id()
        # If token exists, generate a new one
        return token
    return None


def generate_id():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))


def update_ring(philosopher):
    print("Updating ring...")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(2)
        previous_philosopher = tbl.previous_philosopher(philosopher)
        ip = {"message": "new-next-user","ip": philosopher["ip"], "port": philosopher["port"]}
        while True:
            print("Updating ring 2...")
            print(f"IP: {philosopher['ip']}:{philosopher['port']}")
            s.sendto(json.dumps(ip).encode(), (previous_philosopher["ip"], int(previous_philosopher["port"])))
            try:
                data = s.recv(1024)
                if data == b"next-user-accepted":
                    return
            except socket.timeout:
                pass


def generate_new_philosopher(ip, port):
    token = generate_token()
    identifier = generate_id()

    # print(f"Token: {token}")
    # print(f"Identifier: {identifier}")

    new_philosopher = {
        "identifier": identifier,
        "ip": ip,
        "port": port}

    tbl.add_philosopher(new_philosopher)
    next_user = tbl.next_philosopher(new_philosopher)
    update_ring(new_philosopher)

    if token is not None:
        tokens.append(token)
    else:
        token = "None"

    response = ["OK-SEATED", "None", "None", token, identifier, next_user["ip"], next_user["port"]]
    return response


class TableHandler:
    def __init__(self):
        self.log = {}

    def take_seat(self, data):
        # print(f"Data: {data}")
        # data = [message, ip, port, token, identifier, next_token_ip, next_token_port]
        answer = ["ERROR", "None", "None", "None", "None", "None", "None"]
        if len(data) == 7:
            answer = generate_new_philosopher(data[1], data[2])
        return answer

    def hunger(self, data):
        # print(f"Data: {data}")
        # data = [message, ip, port, token, identifier, next_token_ip, next_token_port]
        answer = ["ERROR", "None", "None", "None", "None", "None", "None"]
        if len(data) == 7:
            if tokens.exists(data[3]):
                answer = tbl.hungry(data[4])
        return answer


def main():
    processor = tableService.Processor(TableHandler())
    socket = TSocket.TServerSocket(host=ip_server[0], port=ip_server[1])
    buffer = TTransport.TBufferedTransportFactory()
    protocol = TBinaryProtocol.TBinaryProtocolFactory()

    #server_table = TServer.TSimpleServer(processor, socket, buffer, protocol)
    server_table = TServer.TThreadPoolServer(processor, socket, buffer, protocol)

    print('Server running...')
    server_table.serve()


if __name__ == "__main__":
    main()
