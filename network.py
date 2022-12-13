import socket
from time import sleep


def send_and_receive(s_socket, payload, address, asks, timeout, expected):
    s_socket.settimeout(timeout)
    for i in range(0, asks):
        try:
            s_socket.sendto(payload, address)
            if expected is None:
                sleep(timeout)
                continue
            payload = s_socket.recv(1024)
            if payload == expected:
                return True
        except socket.timeout:
            pass
        except ConnectionResetError:
            print("SOCKET WAS CLOSED BY OUTSIDE FORCES")
            pass
    return False

def send(s_socket, payload, address, attempts):
    for i in range(0, attempts):
        try:
            s_socket.sendto(payload, address)
        except ConnectionResetError:
            print("SOCKET WAS CLOSED BY OUTSIDE FORCES")
            pass
        sleep(0.1)


def receive_and_send(s_socket, payload, timeout, expected):
    s_socket.settimeout(timeout)
    try:
        data, address = s_socket.recvfrom(1024)
        if data == expected:
            if payload is not None:
                s_socket.sendto(payload, address)
            return True
    except socket.timeout:
        pass
    except ConnectionResetError:
        print("SOCKET WAS CLOSED BY OUTSIDE FORCES")
        pass
    print(data)
    return False
