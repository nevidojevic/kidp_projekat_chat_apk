import socket
import threading

from protocol import *


class ChatServer:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((HOST, PORT))
        self.server.listen()

        # shared state: client_socket -> nickname
        self.clients = {}
        self.lock = threading.Lock()

        print(f"Server started on {HOST}:{PORT}")

    def broadcast(self, msg):
        with self.lock:
            clients = list(self.clients.keys())

        for client in clients:
            try:
                client.send(msg)
            except:
                pass

    def handle_client(self, client):
        while True:
            try:
                msg = client.recv(BUFFER_SIZE)

                if not msg:
                    raise Exception()

                decoded = msg.decode(ENCODING)

                if decoded == EXIT:
                    raise Exception()

                self.broadcast(msg)

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
                        f"{nickname} {LEFT}".encode(ENCODING)
                    )
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

            self.broadcast(f"{nickname} {JOINED}".encode(ENCODING))

            client.send(CONNECTED.encode(ENCODING))

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