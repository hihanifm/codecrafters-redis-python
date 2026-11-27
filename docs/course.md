# Course roadmap

Stage titles from the [CodeCrafters "Build your own Redis" overview](https://app.codecrafters.io/courses/redis/overview) (titles only; stage details need login). Core challenge free until 31 Dec 2026.

Legend: [x] done, [ ] to do.

## 1. Basics (7)
- [x] Bind to a port
- [x] Respond to PING
- [x] Respond to multiple PINGs
- [x] Handle concurrent clients
- [x] Implement the ECHO command
- [x] Implement the SET & GET commands
- [x] Expiry

## 2. Lists (11)
- [x] Create a list
- [x] Append an element
- [x] Append multiple elements
- [x] List elements (positive indexes)
- [x] List elements (negative indexes)
- [x] Prepend elements
- [x] Query list length
- [x] Remove an element
- [x] Remove multiple elements
- [x] Blocking retrieval
- [ ] Blocking retrieval with timeout

## 3. Streams (13)
- [ ] The TYPE command
- [ ] Create a stream
- [ ] Validating entry IDs
- [ ] Partially auto-generated IDs
- [ ] Fully auto-generated IDs
- [ ] Query entries from stream
- [ ] Query with -
- [ ] Query with +
- [ ] Query single stream using XREAD
- [ ] Query multiple streams using XREAD
- [ ] Blocking reads
- [ ] Blocking reads without timeout
- [ ] Blocking reads using $

## 4. Transactions (11)
- [ ] The INCR command (1/3)
- [ ] The INCR command (2/3)
- [ ] The INCR command (3/3)
- [ ] The MULTI command
- [ ] The EXEC command
- [ ] Empty transaction
- [ ] Queueing commands
- [ ] Executing a transaction
- [ ] The DISCARD command
- [ ] Failures within transactions
- [ ] Multiple transactions

## 5. Optimistic Locking (8)
- [ ] The WATCH command
- [ ] WATCH inside transaction
- [ ] Tracking key modifications
- [ ] Watching multiple keys
- [ ] Watching missing keys
- [ ] The UNWATCH command
- [ ] Unwatch on EXEC
- [ ] Unwatch on DISCARD

## 6. Replication (18)
- [ ] Configure listening port
- [ ] The INFO command
- [ ] The INFO command on a replica
- [ ] Initial replication ID and offset
- [ ] Send handshake (1/3)
- [ ] Send handshake (2/3)
- [ ] Send handshake (3/3)
- [ ] Receive handshake (1/2)
- [ ] Receive handshake (2/2)
- [ ] Empty RDB transfer
- [ ] Single-replica propagation
- [ ] Multi-replica propagation
- [ ] Command processing
- [ ] ACKs with no commands
- [ ] ACKs with commands
- [ ] WAIT with no replicas
- [ ] WAIT with no commands
- [ ] WAIT with multiple commands

## 7. RDB Persistence (6)
- [ ] RDB file config
- [ ] Read a key
- [ ] Read a string value
- [ ] Read multiple keys
- [ ] Read multiple string values
- [ ] Read value with expiry

## 8. AOF Persistence (10)
- [ ] Default AOF options
- [ ] AOF options from flags
- [ ] Create append-only directory
- [ ] Create append-only file
- [ ] Create manifest file
- [ ] Write a single command
- [ ] Write multiple commands
- [ ] Filter write commands
- [ ] Replay a single command
- [ ] Replay multiple commands

## 9. Pub/Sub (7)
- [ ] Subscribe to a channel
- [ ] Subscribe to multiple channels
- [ ] Enter subscribed mode
- [ ] PING in subscribed mode
- [ ] Publish a message
- [ ] Deliver messages
- [ ] Unsubscribe

## 10. Sorted Sets (8)
- [ ] Create a sorted set
- [ ] Add members
- [ ] Retrieve member rank
- [ ] List sorted set members
- [ ] ZRANGE with negative indexes
- [ ] Count sorted set members
- [ ] Retrieve member score
- [ ] Remove a member

## 11. Bitmaps (9)
- [ ] Create a bitmap
- [ ] Retrieve a bit
- [ ] Read a string as bits
- [ ] Read bits as a string
- [ ] Grow a bitmap
- [ ] Count set bits
- [ ] AND two bitmaps
- [ ] AND bitmaps of different lengths
- [ ] OR two bitmaps

## 12. Geospatial Commands (8)
- [ ] Respond to GEOADD
- [ ] Validate coordinates
- [ ] Store a location
- [ ] Calculate location score
- [ ] Respond to GEOPOS
- [ ] Decode coordinates
- [ ] Calculate distance
- [ ] Search within radius

## 13. Authentication (8)
- [ ] Respond to ACL WHOAMI
- [ ] Respond to ACL GETUSER
- [ ] The nopass flag
- [ ] The passwords property
- [ ] Setting default user password
- [ ] The AUTH command
- [ ] Enforce authentication
- [ ] Authenticate using AUTH
