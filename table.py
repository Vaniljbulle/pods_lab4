import threading
import random
from time import sleep
import monitors


class bcolors:
    ENDC = '\033[0m'


def get_color():
    return f"\033[38;2;{random.randint(0, 255)};{random.randint(0, 255)};{random.randint(0, 255)}m"


class Table:
    def __init__(self):
        self.forks = [threading.Semaphore() for n in range(2)]
        self.philosophers = monitors.ThreadSafeList()

    def add_philosopher(self, philosopher):
        philosopher["color"] = get_color()
        print(
            f"Philosopher {philosopher['color']}{philosopher['ip']}:{philosopher['port']}{bcolors.ENDC} has sat down.")
        self.philosophers.append(philosopher)
        if self.philosophers.__len__() >= 2:
            self.forks.append(threading.Semaphore())

    def remove_philosopher(self, philosopher):
        index = self.philosophers.get_index_by_search("identifier", philosopher["identifier"])
        if self.philosophers.__len__() >= 2:
            self.philosophers.remove_by_index(index)
            self.forks.pop((index + 1) % len(self.forks))

    def gormandize(self):
        sleep(random.randint(3, 10))

    def hungry(self, identifier):
        philosopher = self.philosophers.get_item_by_search("identifi"
                                                           "er", identifier)
        color = philosopher["color"]

        print(f"Philosopher {color}{philosopher['ip']}:{philosopher['port']}{bcolors.ENDC} is hungry.")
        index = self.philosophers.get_index_by_search("identifier", identifier)
        self.forks[index].acquire()  # Acquire the fork to the left
        print(f"Philosopher {color}{philosopher['ip']}:{philosopher['port']}{bcolors.ENDC} has acquired the left fork.")

        indexY = ((self.philosophers.get_index_by_search("identifier", identifier) + 1) % len(self.forks))
        self.forks[indexY].acquire()  # Acquire the fork to the right
        print(
            f"Philosopher {color}{philosopher['ip']}:{philosopher['port']}{bcolors.ENDC} has acquired the right fork.")

        print(f"Philosopher {color}{philosopher['ip']}:{philosopher['port']}{bcolors.ENDC} is gormandizing.")
        self.gormandize()
        print(f"Philosopher {color}{philosopher['ip']}:{philosopher['port']}{bcolors.ENDC} has finished gormandizing.")

        self.forks[
            self.philosophers.get_index_by_search("identifier", identifier)].release()  # Release the fork to the left
        self.forks[(self.philosophers.get_index_by_search("identifier", identifier) + 1) % len(
            self.forks)].release()  # Release the fork to the right
        print(f"Philosopher {color}{philosopher['ip']}:{philosopher['port']}{bcolors.ENDC} has released his forks.")
        print(f"Philosopher {color}{philosopher['ip']}:{philosopher['port']}{bcolors.ENDC} is thinking.")

        return ["GORMANDIZED", "None", "None", "None", "None", "None", "None"]

    def next_philosopher(self, philosopher):
        next_philospher = self.philosophers.get_next(philosopher)
        return next_philospher

    def previous_philosopher(self, philosopher):
        philosopher = self.philosophers.get_previous(philosopher)
        return philosopher
