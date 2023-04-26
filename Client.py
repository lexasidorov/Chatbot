from socket import *

s = socket(AF_INET,SOCK_STREAM)
s.connect(('localhost',8888))

# tm = s.recv(1024)#принимать не более 1024 байт
# s.close()
# print(f"Текущее время: {tm.decode('ascii')}")
while True:
    response = s.recv(4096)
    print(f"Бот: {response.decode('UTF-8')}")
    msg = input('Вы: ')
    s.send(msg.encode('UTF-8'))