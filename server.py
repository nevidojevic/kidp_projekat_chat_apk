import threading
import socket

host="localhost"
port=55555

server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

server.bind((host,port))

server.listen()

#globalne promenljive
clients = {}
clients_lock = threading.Lock()

#broadcast, handle, receive metode
def broadcast(msg):
    # with clients_lock:
    #     for client in clients:
    #         client.send(msg)
    with clients_lock:
        current_clients = list(clients.keys())

    for client in current_clients:
        try:
            client.send(msg)
        except:
            pass

def handle(client):
    while True:
        try:
            msg = client.recv(1024) #probaj da primis poruku klijenta
            if not msg:
                raise Exception()
            if msg.decode("ascii") == "EXIT":
                raise Exception()
            broadcast(msg) #ako radi, posalji svim klijentima
        except:
            nickname = None
            with clients_lock:
                if client in clients:
                    nickname = clients[client]
                    del clients[client]
            client.close()
            if nickname is not None:
                broadcast(f"{nickname} has left the chat.".encode("ascii"))
                print(f"{nickname} disconnected.")
            break

def receive():
    while True:
        client, address=server.accept()
        print(f'Connected with {str(address)}')
        client.send('NICK'.encode('ascii'))
        nickname=client.recv(1024).decode('ascii')
        with clients_lock:
            clients[client] = nickname
        print(f'Nickname of the client is {nickname}.')
        broadcast(f'{nickname} has joined the chat.'.encode('ascii'))
        client.send('Connected to the server!'.encode('ascii'))

        thread=threading.Thread(target=handle, args=(client,))
        thread.start()
print('Server is ready.')
try:
    receive()
except KeyboardInterrupt:
    print("\nShutting down server...")

    with clients_lock:
        current_clients = list(clients.keys())

    for client in current_clients:
        client.close()

    server.close()

    print("Server stopped.")