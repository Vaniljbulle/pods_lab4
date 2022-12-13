import threading
from time import sleep

from zero import ZeroClient

zero_client = ZeroClient("192.168.1.167", 3000)


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


def request_seat(my_ip, my_port):
    print(f"Seat requested")
    payload = {"message": "LET-ME-SIT",
               "address": (my_ip, my_port)}
    r = zero_client.call("take_seat", payload)
    return r


def wait_token():
    if token.get() is None:
        print("I am waiting for a token.", end="")
        while token.get() is None:
            print(" . ", end="", flush=True)
            sleep(1)
    print(f"I got a token! {token.get()}")


def hunger():
    print("\nI am hungry")
    wait_token()
    r = zero_client.call("hunger", {"token": token.get(), "identifier": identifier})
    return r


if __name__ == "__main__":
    token = Monitor()
    next_user = Monitor()
    identifier = None

    while True:
        ans = request_seat("18561891", 5151)
        if ans is not None:
            if ans["message"] == "OK-SEATED":
                print("We got a seat!")
                token.set(ans["token"])
                next_user.set(ans["next_token_user_address"])
                identifier = ans["identifier"]
                break
        sleep(1)

    sleep(1)
    while True:
        ans = hunger()
        print(ans)
        break
