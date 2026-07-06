import socket
import threading

from protocol import *


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.nickname = ""

        self.connected = False

        # Buffer za poruke primljene posle NICK/nickname razmene, jer server
        # može poslati više poruka zaredom (istorija, lista korisnika) bez
        # čekanja odgovora, a TCP ne čuva granice poruka.
        self.buffer = ""

        # Funkcije koje će GUI proslediti
        # Pozivaju se svaki put kada stigne nova poruka / lista korisnika
        self.on_message = None
        self.on_userlist = None

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
                chunk = self.client.recv(BUFFER_SIZE)

                if not chunk:
                    break

                self.buffer += chunk.decode(ENCODING)

                while DELIM in self.buffer:
                    message, self.buffer = self.buffer.split(DELIM, 1)

                    if message:
                        self.dispatch(message)

            except Exception as e:

                print("Receive error:", e)

                break

        self.connected = False
        self.client.close()

    def dispatch(self, message):
        if message.startswith(LIST + SEP):
            nicknames = message[len(LIST) + 1:].split(",")
            nicknames = [n for n in nicknames if n]

            if self.on_userlist:
                self.on_userlist(nicknames)

        elif message.startswith(PRIV + SEP):
            _, target, text = message.split(SEP, 2)

            if self.on_message:
                self.on_message(f"[Private] {text}")

        elif self.on_message:
            self.on_message(message)

    def send(self, text):
        if not self.connected:
            return

        message = f"{self.nickname}: {text}"

        self.client.send(message.encode(ENCODING))

    def send_private(self, target, text):
        if not self.connected:
            return

        message = f"{PRIV}{SEP}{target}{SEP}{self.nickname}: {text}"

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