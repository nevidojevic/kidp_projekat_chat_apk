import threading
import socket

nickname=input("Choose a nickname: ")

client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect(('localhost',55555))

def receive():
    while True:
        try:
            msg=client.recv(1024).decode('ascii')
            if msg=='NICK':
                client.send(nickname.encode('ascii'))
            else:
                print(msg)
        except:
            print('error occurred')
            client.close()
            break

def write():
    while True:
        msg=f'{nickname}:{input("")}'
        client.send(msg.encode('ascii'))

receive_thread=threading.Thread(target=receive)
receive_thread.start()

write_thread=threading.Thread(target=write)
write_thread.start()
