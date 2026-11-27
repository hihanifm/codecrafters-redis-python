"""One function per command: args in, RESP reply bytes out. No sockets here."""

import threading
from collections import deque
from itertools import islice

from app import resp
from app.ranges import redis_range_to_python_slice
from app.store import get_or_create_list, now_ms, store, store_lock, waiters


def ping(args):
    return resp.simple(b"PONG")


def echo(args):
    return resp.bulk(args[0])


def set_(args):
    deadline = 0  # 0 = no expiry
    if len(args) > 3 and args[2].upper() == b"PX":
        px = int(args[3])
        if px <= 0:
            return resp.error(b"ERR invalid expire time in 'set' command")
        deadline = now_ms() + px
    with store_lock:
        store[args[0]] = (args[1], deadline)
    return resp.simple(b"OK")


def get(args):
    value = None
    with store_lock:  # check + delete must be one step
        record = store.get(args[0])
        if record is not None:
            value, deadline = record
            if deadline != 0 and now_ms() > deadline:  # expired: lazy delete
                del store[args[0]]
                value = None
    return resp.bulk(value)


def serve_waiters(key, items):
    # caller must hold store_lock. Pusher pops on the waiter's behalf, so no other
    # client can steal the value between wake-up and the waiter re-taking the lock.
    queue = waiters.get(key)
    while queue and items:
        waiter = queue.popleft()  # oldest blocked client first (FIFO fairness)
        waiter["value"] = items.popleft()  # fill the slot before waking
        waiter["event"].set()
    if queue is not None and not queue:
        del waiters[key]
    if not items:
        del store[key]  # empty list = no key


def rpush(args):
    with store_lock:  # get-or-create + append + hand-off must be one step
        items = get_or_create_list(args[0])
        items.extend(args[1:])  # all values in one step
        length = len(items)  # Redis reports length after push, before serving waiters
        serve_waiters(args[0], items)
    return resp.integer(length)


def lpush(args):
    with store_lock:  # get-or-create + prepend + hand-off must be one step
        items = get_or_create_list(args[0])
        items.extendleft(args[1:])  # appendleft each in order: a b c -> [c, b, a]
        length = len(items)
        serve_waiters(args[0], items)
    return resp.integer(length)


def llen(args):
    with store_lock:
        record = store.get(args[0])
        length = len(record[0]) if record else 0  # missing key = empty list
    return resp.integer(length)


def lpop(args):
    count = int(args[1]) if len(args) > 1 else None  # no count -> bulk reply, count -> array
    values = None
    with store_lock:  # pop + delete-if-empty must be one step
        record = store.get(args[0])
        if record:
            items = record[0]
            n = 1 if count is None else min(count, len(items))  # ask for more than exist -> get what's there
            values = [items.popleft() for _ in range(n)]
            if not items:
                del store[args[0]]  # empty list = no key
    if count is None:
        return resp.bulk(values[0] if values else None)  # None -> nil, distinct from "" element
    return resp.array(values)  # None -> null array


def blpop(args):
    key = args[0]  # single key, timeout 0 (block forever) for now
    with store_lock:
        record = store.get(key)
        if record:  # data ready: behave like LPOP
            value = record[0].popleft()
            if not record[0]:
                del store[key]
            return resp.array([key, value])
        waiter = {"event": threading.Event(), "value": None}
        waiters.setdefault(key, deque()).append(waiter)  # join the line for this key
    waiter["event"].wait()  # sleep outside the lock; pusher fills value before set()
    return resp.array([key, waiter["value"]])


def lrange(args):
    start, stop = int(args[1]), int(args[2])
    with store_lock:
        record = store.get(args[0])
        if record:
            py_start, py_stop = redis_range_to_python_slice(start, stop, len(record[0]))
            # deque has no slicing; islice walks from the left (O(stop), like Redis's O(S+N))
            # list() copies, so the reply is built after releasing the lock
            values = list(islice(record[0], py_start, py_stop))
        else:
            values = []
    return resp.array(values)


COMMANDS = {
    b"PING": ping,
    b"ECHO": echo,
    b"SET": set_,
    b"GET": get,
    b"RPUSH": rpush,
    b"LPUSH": lpush,
    b"LLEN": llen,
    b"LPOP": lpop,
    b"BLPOP": blpop,
    b"LRANGE": lrange,
}


def execute(name, args):
    handler = COMMANDS.get(name.upper())
    if handler is None:
        return resp.error(b"ERR unknown command '%s'" % name)
    return handler(args)
