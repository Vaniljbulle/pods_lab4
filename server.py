import random
import socketserver
import string
import threading
from time import sleep
import table
import json
import network as nw

ip = ("192.168.1.167", 3000)


def generate_token():
    if tb.philosophers.__len__() != 1:
        token = generate_id()
        while token in tokens:
            token = generate_id()
        return token
    else:
        return None


def generate_id():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))


tokens = []
tb = table.Table()


class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        payload = self.request[0].strip().decode()
        socket = self.request[1]

        try:
            payload = json.loads(payload)
        except json.decoder.JSONDecodeError:
            return

        if payload["message"] == "LET-ME-SIT":
            token = generate_token()
            identifier = generate_id()

            philosopher = {
                "identifier": identifier,
                "address": self.client_address,
            }
            tb.add_philosopher(philosopher)

            if token is not None:
                tokens.append(token)

            response = {
                "identifier": identifier,
                "token": token,
                "next_token_user_address": tb.next_philosopher(philosopher),
                "message": "OK-SIT"
            }

            print(f"Philosopher {self.client_address} requested a seat.")
            if not nw.send_and_receive(socket, json.dumps(response).encode(), self.client_address, 5, 1, b"SIT-OK"):
                print(f"Philosopher {self.client_address} did not accept the seat.")
                tb.remove_philosopher(philosopher)
                if token is not None:
                    tokens.remove(token)
            else:
                print(f"Philosopher {self.client_address} is sitting at the table.")
        elif payload["message"] == "HUNGRY":
            tkn = payload["token"]
            if tkn is not None and tkn in tokens:
                sleep(0.1)
                socket.sendto(b"OK", self.client_address)
                tb.hungry(payload["identifier"])
                socket.sendto(b"GORMANDIZED", self.client_address)


class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass


def UDPServer():
    server = ThreadedUDPServer(ip, ThreadedUDPRequestHandler)

    try:
        print(f"Server started on {ip}")
        with server:
            # Threaded UDP Server to accept orders
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()

            print(f"Server loop running in thread: {server_thread.name}")

            # Coffee machine go brrrr
            while True:
                pass

    except KeyboardInterrupt:
        print("Server shutting down")
        # server_thread.join()
        server.shutdown()
        server.server_close()


def main():
    UDPServer()


if __name__ == '__main__':
    main()
