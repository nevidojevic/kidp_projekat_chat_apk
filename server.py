import socket
import threading
from collections import deque

from protocol import *


class ChatServer:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((HOST, PORT))
        self.server.listen()

        # shared state: client_socket -> nickname
        self.clients = {}
        # shared state: last 20 broadcast chat messages (raw wire bytes)
        self.history = deque(maxlen=20)
        self.lock = threading.Lock()

        print(f"Server started on {HOST}:{PORT}")

    def broadcast(self, msg):
        with self.lock:
            self.history.append(msg)
            clients = list(self.clients.keys())

        for client in clients:
            try:
                client.send(msg)
            except:
                pass

    def broadcast_userlist(self):
        with self.lock:
            nicknames = list(self.clients.values())
            clients = list(self.clients.keys())

        msg = f"{LIST}{SEP}{','.join(nicknames)}{DELIM}".encode(ENCODING)

        for client in clients:
            try:
                client.send(msg)
            except:
                pass

    def find_client(self, nickname):
        with self.lock:
            for sock, nick in self.clients.items():
                if nick == nickname:
                    return sock
        return None

    def handle_client(self, client):
        while True:
            try:
                msg = client.recv(BUFFER_SIZE)

                if not msg:
                    raise Exception()

                decoded = msg.decode(ENCODING)

                if decoded == EXIT:
                    raise Exception()

                if decoded.startswith(PRIV + SEP):
                    _, target, text = decoded.split(SEP, 2)
                    target_sock = self.find_client(target)

                    if target_sock:
                        priv_msg = f"{PRIV}{SEP}{target}{SEP}{text}{DELIM}".encode(ENCODING)
                        try:
                            target_sock.send(priv_msg)
                        except:
                            pass
                        try:
                            client.send(priv_msg)
                        except:
                            pass
                    else:
                        try:
                            client.send(f"[System] User '{target}' not found.{DELIM}".encode(ENCODING))
                        except:
                            pass

                    continue

                self.broadcast(msg + DELIM.encode(ENCODING))

            except:
                nickname = None

                with self.lock:
                    if client in self.clients:
                        nickname = self.clients.pop(client)

                try:
                    client.close()
                except:
                    pass

                if nickname:
                    self.broadcast(
                        f"{nickname} {LEFT}{DELIM}".encode(ENCODING)
                    )
                    self.broadcast_userlist()
                    print(f"{nickname} disconnected")

                break

    def receive(self):
        while True:
            client, address = self.server.accept()
            print(f"Connected: {address}")

            client.send(NICK.encode(ENCODING))
            nickname = client.recv(BUFFER_SIZE).decode(ENCODING)

            with self.lock:
                self.clients[client] = nickname

            print(f"Nickname: {nickname}")

            self.broadcast(f"{nickname} {JOINED}{DELIM}".encode(ENCODING))

            client.send((CONNECTED + DELIM).encode(ENCODING))

            with self.lock:
                history = list(self.history)

            for line in history:
                try:
                    client.send(line)
                except:
                    pass

            self.broadcast_userlist()

            thread = threading.Thread(
                target=self.handle_client,
                args=(client,),
                daemon=True
            )
            thread.start()

    def start(self):
        try:
            self.receive()
        except KeyboardInterrupt:
            print("\nShutting down server...")

            with self.lock:
                clients = list(self.clients.keys())

            for c in clients:
                try:
                    c.close()
                except:
                    pass

            self.server.close()
            print("Server stopped.")


if __name__ == "__main__":
    server = ChatServer()
    server.start()