import threading
import queue
import random
from time import sleep
import network as nw


class bcolors:
    ENDC = '\033[0m'


class ThreadSafeList:
    def __init__(self):
        self.lock = threading.Lock()
        self.list = []

    def append(self, item):
        with self.lock:
            self.list.append(item)

    def pop(self, philosopher):
        with self.lock:
            index = self.list.index(philosopher)
            return self.list.pop(index)

    def get(self, index):
        with self.lock:
            return self.list[index]

    def get_next(self, philosopher):
        with self.lock:
            index = self.list.index(philosopher)
            if index == len(self.list) - 1:
                return self.list[0]
            else:
                return self.list[index + 1]

    def get_previous(self, philosopher):
        with self.lock:
            index = self.list.index(philosopher)
            if index == 0:
                return self.list[len(self.list) - 1]
            else:
                return self.list[index - 1]

    def __len__(self):
        with self.lock:
            return len(self.list)

    def __iter__(self):
        with self.lock:
            return iter(self.list)

    def index(self, philosopher):
        with self.lock:
            return self.list.index(philosopher)

    def index_identifier(self, identifier):
        with self.lock:
            for i in range(0, len(self.list)):
                if self.list[i]["identifier"] == identifier:
                    return i
            return -1


class Table:
    def __init__(self):
        self.forks = [threading.Semaphore() for n in range(2)]
        self.philosophers = ThreadSafeList()

    def add_philosopher(self, philosopher):
        philosopher["color"] = self.get_color()
        self.philosophers.append(philosopher)
        if self.philosophers.__len__() >= 2:
            self.forks.append(threading.Semaphore())

    def remove_philosopher(self, philosopher):
        self.philosophers.pop(philosopher)
        if self.philosophers.__len__() >= 2:
            self.forks.pop()

    def get_philosopher(self, philosopher):
        return self.philosophers.get(philosopher)

    def gormandize(self, identifier):
        sleep(random.randint(1, 20))

    def hungry(self, identifier):
        index = self.philosophers.index_identifier(identifier)
        color = self.philosophers.get(index)["color"]

        print(f"Philosopher {color}{identifier}{bcolors.ENDC} is hungry.")

        self.forks[index].acquire()  # Acquire the fork to the left
        print(f"Philosopher {color}{identifier}{bcolors.ENDC} has acquired left fork. [{index}]")

        self.forks[(index + 1) % len(self.forks)].acquire()  # Acquire the fork to the right
        print(f"Philosopher {color}{identifier}{bcolors.ENDC} has acquired right fork. [{(index + 1) % len(self.forks)}]")

        print(f"Philosopher {color}{identifier}{bcolors.ENDC} is gormandizing.")
        self.gormandize(identifier)
        print(f"Philosopher {color}{identifier}{bcolors.ENDC} is done gormandizing.")

        print(f"Philosopher {color}{identifier}{bcolors.ENDC} released both forks and is now thinking.")
        self.forks[index].release()  # Release the fork to the left
        self.forks[(index + 1) % len(self.forks)].release()  # Release the fork to the right

    def next_philosopher(self, philosopher):
        philosopher = self.philosophers.get_next(philosopher)
        return philosopher["address"]

    def get_color(self):
        return f"\033[38;2;{random.randint(0, 255)};{random.randint(0, 255)};{random.randint(0, 255)}m"

    def previous_philosopher(self, philosopher):
        philosopher = self.philosophers.get_previous(philosopher)
        return philosopher["address"]


