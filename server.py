import threading
import socket

host="localhost"
port=55555

server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

server.bind((host,port))

server.listen()

#broadcast, handle, receive metode
clients=[]
nicknames=[]

def broadcast(msg):
    for client in clients:
        client.send(msg)

def handle(client):
    while True:
        try:
            msg = client.recv(1024) #probaj da primis poruku klijenta
            broadcast(msg) #ako radi, posalji svim klijentima
        except:
            index=clients.index(client) #uzimamo indeks klijenta gde je pukla petlja
            clients.remove(client) #uklanjamo klijenta
            client.close()
            nickname=nicknames[index]
            broadcast(f'{nickname} has left the chat.'.encode('ascii'))
            nicknames.remove(nickname) #uklanjamo i nadimak klijenta
            break

def receive():
    while True:
        client, address=server.accept()
        print(f'Connected with {str(address)}')
        client.send('NICK'.encode('ascii'))
        nickname=client.recv(1024).decode('ascii')
        clients.append(client)
        print(f'Nickname of the client is {nickname}.')
        broadcast(f'{nickname} has joined the chat.'.encode('ascii'))
        client.send('Connected to the server!'.encode('ascii'))

        thread=threading.Thread(target=handle, args=(client,))
        thread.start()
print('Server is ready.')
receive()