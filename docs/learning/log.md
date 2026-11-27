# Redis learning log

Running notes from building Redis in Python (CodeCrafters, `~/work/codecrafters-redis-python`) with Claude Code as tutor. A few lines per stage: concept, questions Hanif asked, backend angle. Source for per-chapter revision pages (`NN-<chapter>.html`), later interview prep and Medium drafts. Private; not committed or pushed automatically.

## Chapter 1: Basics (completed 2026-11-25)

### Bind to a port
- `socket.create_server(("localhost", 6379))` + `accept()` waits for one client.
- Tooling: `codecrafters submit` = remote tests + commit + push + advance; `codecrafters test` = debug only.

### Respond to PING / multiple PINGs
- RESP (**RE**dis **S**erialization **P**rotocol): simple string `+PONG\r\n`.
- `recv` returns `b""` on clean close → must break, or loop crashes server. Abrupt reset raises `ConnectionResetError`.
- Q: is `/` or `/n` the delimiter? → `\r\n` (CRLF), backslash is escape syntax; every RESP item gets its own line.
- Q: can `split` keep the delimiter? → `splitlines(keepends=True)`, `re.split` with capture group, `partition`.

### Concurrent clients
- Thread per client: `threading.Thread(target=handle_client, args=(conn,))`.
- GIL: only one thread runs Python at a time; fine for I/O-bound servers (released during `recv`).
- Backend angle: real Redis is single-threaded + event loop (no locks needed); since 6.0, threaded network I/O.

### ECHO
- Request = RESP array of bulk strings: `*2\r\n$4\r\nECHO\r\n$3\r\nhey\r\n`. Reply bulk string `$3\r\nhey\r\n`.
- `[2::2]` slice = start 2, every 2nd → skips header and length lines.
- Commands case-insensitive (`.upper()`). Unknown command → `-ERR unknown command 'FOO'`.

### SET / GET
- Global dict shared by all threads; missing key → null bulk `$-1\r\n`.
- Q: does GIL mean no sync needed? → No. Single dict op is atomic; compound read-modify-write (`x = x + 1`) races. Use `threading.Lock`. GIL safety is a CPython detail, not a language promise. Free-threaded Python 3.13+/3.14 removes GIL.
- Q: skip read lock = eventual consistency? → No; that term is for distributed replicas. Lock-free single reads are still consistent here; torn reads appear with multi-key writes.
- Decision: lock both reads and writes. Keep critical sections short; send outside the lock.

### Expiry (PX)
- Hanif's design: store `(value, deadline)`, check on GET, delete if expired = **lazy expiration** (what real Redis does, plus periodic active sweep).
- Store absolute deadline (`now + ttl`), not TTL. Terms: elapsed / TTL / deadline.
- `time.monotonic()` (never jumps) vs `time.time()` (wall clock, can jump). Redis uses wall-clock ms because it persists to disk.
- Check-then-delete = compound op → one lock.
- Tangent: Redis written in C (antirez, 2009); timeline 2.6 Lua, 3.0 Cluster, 5.0 Streams, 6.0 ACL/TLS/RESP3, 2024 license change → Valkey fork. ACLs ↔ least privilege for agents.

## Chapter 2: Lists (in progress)

### Create list / append (RPUSH)
- RESP integer `:1\r\n` (list length).
- Record = `(list, deadline)`; tuple read-only but list inside mutable (reference). Renamed `entry` → `record`.
- Expiry belongs to key, not type: lists expire via `EXPIRE`/`PEXPIRE`.
- Get-or-create + append under one lock = check-then-act (DB equivalent: upsert). Multi-value RPUSH atomic: `extend(args[1:])`.
- Backend angle: Redis has one typed keyspace; wrong type → `WRONGTYPE` error.

### LRANGE (positive + negative indexes)
- Redis stop inclusive, Python slice stop exclusive → `stop + 1`. Python slices clamp, never throw (indexing does).
- Negative = another *name* for a position, not a direction. Read direction always left→right; `-3 -5` → empty.
- Two stages: **normalize** (`len + idx`; start still negative → 0; stop still negative → empty) then **translate** (`+1`).
- Only `stop = -1` breaks naive `+1` (crosses zero).
- Why negatives exist: "last N" = `-N -1` in one atomic command; otherwise `LLEN` + `LRANGE` = two round trips + race. Uses: activity feeds, `LTRIM -100 -1` capped logs.
- Method: TDD red→green; equivalence partitioning (happy path, stop past end, start past end, both); table-driven tests with `subTest`. Pure function `redis_range_to_python_slice` in `app/ranges.py`.
- Renamed `items` → `name, *args`.
- Pace note: deep-dived edge cases by hand; good once per pattern, then move on.

### Prepend (LPUSH)
- `LPUSH k a b c` → `[c, b, a, ...old]`: each value pushed onto head in arg order. Mix with RPUSH freely: RPUSH+LPOP = FIFO queue, LPUSH+LPOP = stack, LPUSH on a FIFO queue = crude priority lane.
- Python `list` = dynamic array: append amortized O(1), `insert(0)` O(n) (shift everything). CPython grows ~1/8 + 6, rounded to 4 → memory vs time tradeoff (vs 2× elsewhere).
- Amortized ≠ never slow: rare resize still a latency spike (p99). Redis rehashes its hash table incrementally for the same reason.
- Switched store to `collections.deque` (blocks of 64, doubly linked): O(1) both ends, O(n) middle — same tradeoff as Redis lists. `extendleft(args)` = appendleft each in order. No slicing → LRANGE uses `islice` (O(stop), matches Redis O(S+N)). Range helper untouched: clean interface, swapped container.
- Shared `get_or_create_list` helper (caller holds lock). Whole multi-value push under lock = atomic.
