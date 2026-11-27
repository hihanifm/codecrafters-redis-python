"""Shared keyspace. Records are (value, deadline_ms); deadline 0 = no expiry."""

import threading
import time
from collections import deque

store = {}  # shared by all client threads
store_lock = threading.Lock()  # guards every access to store and waiters
waiters = {}  # key -> deque of blocked-client slots {"event", "value"}, oldest first


def now_ms():
    return time.monotonic() * 1000


def get_or_create_list(key):
    # caller must hold store_lock
    record = store.get(key)
    if record is None:
        record = (deque(), 0)  # new list, no expiry; O(1) push at both ends
        store[key] = record
    return record[0]
