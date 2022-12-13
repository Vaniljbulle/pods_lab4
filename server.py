import random
import string
import typing
from time import sleep

from zero import ZeroServer
import table


class global_vars:
    tb = table.Table()
    tokens = []


def generate_token():
    if global_vars.tb.philosophers.__len__() != 1:
        token = generate_id()
        # If token exists, generate a new one
        while token in global_vars.tokens:
            token = generate_id()
        return token
    return None


def generate_id():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))


def generate_new_philosopher(address):
    token = generate_token()
    identifier = generate_id()

    print(f"Token: {token}")
    print(f"Identifier: {identifier}")

    new_philosopher = {"identifier": identifier, "address": address}
    global_vars.tb.add_philosopher(new_philosopher)
    next_user = global_vars.tb.next_philosopher(new_philosopher)

    if token is not None:
        global_vars.tokens.append(token)

    data = {"message": "OK-SEATED",
            "identifier": identifier,
            "token": token,
            "next_token_user_address": next_user}

    return data

ssss = "YOLO"
def take_seat(msg: typing.Dict) -> typing.Dict:
    global ssss
    ssss = "PELLE"
    payload = generate_new_philosopher(msg["address"])
    return payload


def validate_token(tkn):
    print("YO" + ssss)
    global_vars.tb.philosophers.print()
    print(f"1Token: {tkn}")
    print(f"1Tokens: {global_vars.tokens}")
    if tkn in global_vars.tokens:
        return True
    else:
        return False


def hunger(msg: typing.Dict) -> typing.Dict:
    if validate_token(msg["token"]):
        global_vars.tb.hungry(msg["identifier"])
    else:
        return {"message": "INVALID-TOKEN"}


if __name__ == "__main__":
    app = ZeroServer(port=3000, host="192.168.1.167")
    app.register_rpc(take_seat)
    app.register_rpc(hunger)
    app.run()
