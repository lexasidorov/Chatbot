from socket import *

s = socket(AF_INET,SOCK_STREAM)
s.connect(('localhost',8888))

while True:
    response = s.recv(40960)
    print(f"Бот: {response.decode('UTF-8')}")
    msg = input('Вы: ')
    s.send(msg.encode('UTF-8'))