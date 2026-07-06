HOST = "localhost"
PORT = 55555

BUFFER_SIZE = 1024
ENCODING = "ascii"

NICK = "NICK"
EXIT = "EXIT"

CONNECTED = "Connected to the server!"
JOINED = "has joined the chat."
LEFT = "has left the chat."

SEP = "|"
LIST = "LIST"
PRIV = "PRIV"
PRIVATE_CMD = "/w"

# Delimiter between messages sent after the NICK/nickname handshake, needed
# because the server can send several messages back-to-back (history replay,
# user list) with no client round-trip in between, and TCP does not preserve
# message boundaries.
DELIM = "\n"