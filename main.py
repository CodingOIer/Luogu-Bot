import urllib
import pickle
import requests
import threading
import datetime
import time
import pytz
import json
import openai
import random
import string
import luoguapi


class Dict:
    def __init__(self):
        self.data = {}

    def __getitem__(self, index):
        if isinstance(index, tuple) and len(index) == 2:
            if isinstance(index[0], int) and isinstance(index[1], str):
                first_level = self.data.get(index[0], {})
                return first_level.get(index[1], False)
        raise KeyError("Invalid index")

    def __setitem__(self, index, value):
        if isinstance(index, tuple) and len(index) == 2:
            if isinstance(index[0], int) and isinstance(index[1], str):
                if isinstance(value, bool):
                    if index[0] not in self.data:
                        self.data[index[0]] = {}
                    self.data[index[0]][index[1]] = value
                    return
        raise KeyError("Invalid index or value")

    def save(self, filename):
        try:
            with open(filename, 'wb') as file:
                pickle.dump(self.data, file)
        except:
            pass

    @classmethod
    def load(cls, filename):
        try:
            with open(filename, 'rb') as file:
                data = pickle.load(file)
            instance = cls()
            instance.data = data
            return instance
        except:
            pass


class Queue:
    def __init__(self):
        self.queue = []

    def push(self, item):
        self.queue.append(item)

    def front(self):
        if len(self.queue) < 1:
            return None
        return self.queue.pop(0)

    def empty(self):
        return len(self.queue) == 0

    def size(self):
        return len(self.queue)

    def find(self, item):
        return item in self.queue


class Set:
    def __init__(self, iterable=None):
        if iterable is None:
            self._data = {}
        else:
            self._data = {item: None for item in iterable}

    def insert(self, item):
        self._data[item] = None

    def erase(self, item):
        if item in self._data:
            del self._data[item]

    def find(self, item):
        return item in self._data

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __repr__(self):
        return '{' + ', '.join(map(str, self._data)) + '}'

    def __eq__(self, other):
        if isinstance(other, Set):
            return self._data == other._data
        return False


def rmb(s, t):
    index = s.find(t)
    if index == -1:
        return s
    return s[index + len(t):]


def rma(s, t):
    index = s.find(t)
    if index == -1:
        return s
    return s[:index]


def decodeUrl(s):
    return urllib.parse.unquote(s)


def decideUnicode(s):
    return s.encode().decode('unicode_escape')


def rs(length=8):
    char = string.ascii_letters + string.digits
    res = ''.join(random.choice(char) for _ in range(length))
    return res


bot = luoguapi.session()
