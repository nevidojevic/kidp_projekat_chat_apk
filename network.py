import socket
import threading

from protocol import *


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.nickname = ""

        self.connected = False

        # Funkcija koju će GUI proslediti
        # Poziva se svaki put kada stigne nova poruka
        self.on_message = None

    def connect(self, nickname):
        self.nickname = nickname

        self.client.connect((HOST, PORT))

        # Server prvo traži nadimak
        message = self.client.recv(BUFFER_SIZE).decode(ENCODING)

        if message == NICK:
            self.client.send(nickname.encode(ENCODING))

        self.connected = True

        threading.Thread(target=self.receive, daemon=True).start()

    def receive(self):
        while self.connected:
            try:
                message = self.client.recv(BUFFER_SIZE)

                if not message:
                    continue

                message = message.decode(ENCODING)

                if self.on_message:
                    self.on_message(message)


            except Exception as e:

                print("Receive error:", e)

                break

        self.connected = False
        self.client.close()

    def send(self, text):
        if not self.connected:
            return

        message = f"{self.nickname}: {text}"

        self.client.send(message.encode(ENCODING))

    def disconnect(self):
        if not self.connected:
            return

        try:
            self.client.send(EXIT.encode(ENCODING))
        except:
            pass

        self.connected = False

        self.client.close()