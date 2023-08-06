from math import log
from time import sleep


def _default_waiter_function(i):
    return int(log(i + 3)**2)


def waiter():
    i = 1
    while True:
        sleep(_default_waiter_function(i))
        i += 1
        yield


class MangroveResourceDelete(Exception):
    pass
