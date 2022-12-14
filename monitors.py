import threading


class ThreadSafeList:
    def __init__(self):
        self.lock = threading.Lock()
        self.list = []

    def __len__(self):
        with self.lock:
            return len(self.list)

    def append(self, item):
        with self.lock:
            self.list.append(item)

    def get_item_by_index(self, index):
        with self.lock:
            return self.list[index]

    def get_item_by_search(self, key, value):
        with self.lock:
            for item in self.list:
                if item[key] == value:
                    return item
            return None

    def get_index_by_search(self, key, value):
        with self.lock:
            for i in range(0, len(self.list)):
                if self.list[i][key] == value:
                    return i
            return -1

    def get_next(self, item):
        with self.lock:
            for i in range(0, len(self.list)):
                if self.list[i] == item:
                    if i == len(self.list) - 1:
                        return self.list[0]
                    return self.list[i + 1]

    def get_previous(self, item):
        with self.lock:
            for i in range(0, len(self.list)):
                if self.list[i] == item:
                    if i == 0:
                        return self.list[len(self.list) - 1]
                    return self.list[i - 1]


    def remove_by_index(self, index):
        with self.lock:
            self.list.pop(index)

    def remove_item(self, item):
        with self.lock:
            for i in range(0, len(self.list)):
                if self.list[i] == item:
                    self.list.pop(i)
                    return True
            return False

    def exists(self, item):
        with self.lock:
            for i in range(0, len(self.list)):
                if self.list[i] == item:
                    return True
            return False


class ThreadSafeVariable:
    def __init__(self):
        self.lock = threading.Lock()
        self.variable = None

    def set(self, new_value):
        with self.lock:
            self.variable = new_value

    def get(self):
        with self.lock:
            return self.variable

    def clear(self):
        with self.lock:
            self.variable = None

    def replace(self, new_value):
        with self.lock:
            old_value = self.variable
            self.variable = new_value
            return old_value

    def is_set(self):
        with self.lock:
            return self.variable is not None
