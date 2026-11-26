def redis_range_to_python_slice(start, stop, length):
    """Convert Redis LRANGE (start, stop) — inclusive, may be negative —
    into a Python slice (start, stop) — exclusive stop."""
    # normalize: negative index -> its positive twin (-1 -> last)
    if start < 0:
        start += length
    if stop < 0:
        stop += length
    # still negative = before the list
    if start < 0:
        start = 0  # range begins before list: clamp to first item
    if stop < 0:
        return (0, 0)  # range ends before list: nothing to return

    # translate: Redis stop inclusive -> Python stop exclusive
    return (start, stop + 1)
