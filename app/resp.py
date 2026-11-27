"""RESP protocol: parse requests, encode replies."""


def parse_command(data):
    # *N\r\n$len\r\nitem\r\n... -> values are every 2nd part after the array header
    return data.split(b"\r\n")[2::2]


def simple(s):
    return b"+%s\r\n" % s


def error(msg):
    return b"-%s\r\n" % msg


def integer(n):
    return b":%d\r\n" % n


def bulk(value):
    if value is None:
        return b"$-1\r\n"  # null bulk string, redis-cli shows (nil)
    return b"$%d\r\n%s\r\n" % (len(value), value)


def array(values):
    if values is None:
        return b"*-1\r\n"  # null array
    return b"*%d\r\n" % len(values) + b"".join(bulk(v) for v in values)
