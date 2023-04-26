from socket import *
import time
from urllib.request import urlopen
import requests
from xml.etree import ElementTree as ET

def take_response():
    response = client.recv(1024)  # получаем данные от клиента
    r = response.decode('UTF-8')
    return r

s = socket(AF_INET,SOCK_STREAM) # создадим объект сокета (сетевой, потоковый)
s.bind(("",8888)) #настраиваем сокет на локальный IP и порт
s.listen(5) #режим ожидания, <=5 запросов одновременно


client,addr = s.accept()    #принимаем запрос на соединение
print(f"Получен запрос на соединение {str(addr)}")
hello = (
    'Меню:\n'
    '1 - узнать время\n'
    '2 - курс доллара\n3 - операции с числами\n'
    '4 - рассказать анекдот\n'
)
client.send(hello.encode('UTF-8'))  #отправляем первое сообщение

while True:
    r1 = take_response()
    if r1 == '1':
        timestr = time.ctime(time.time()) + "\n"    # формируем строку с текущей датой и временем
        client.send(timestr.encode('ascii'))
    elif r1 == '2':
        rate_usd = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()    # получаем словарь
        rate_usd_rrf = rate_usd['Valute']['USD']['Value']    # находим значение по ключам
        msg = (f'Курс доллара {rate_usd_rrf}')
        client.send(msg.encode('UTF-8'))
    elif r1 == '3':
        msg = 'Введите математическое выражение'
        client.send(msg.encode('UTF-8'))
        r2 = take_response()
        try:
            msg = f'{r2} = {eval(r2)}' # вычисляем мат.выражение
            client.send(msg.encode('UTF-8'))
        except:
            msg = "Некорректное выражение"  # возвращаем сообщение об ошибке
            client.send(msg.encode('UTF-8'))
    elif r1 == '4':
        with urlopen('http://rzhunemogu.ru/Rand.aspx?CType=1') as r:
            xml_element = (ET.fromstring(r.read(), ET.XMLParser(encoding='Windows-1251'))) # создаем xml элемент
            for i in xml_element:
                joke = i.text
        msg = f"Рассказываю шутку:\n{joke}"
        client.send(msg.encode('UTF-8'))
    # elif r1 == '5':
    #     bank = 0
    #     bet = 0
    #     while True:
    #         msg = f'Ваш счёт в игре: {bank}.\nВведите вашу ставку или введите 0 для выхода.'
    #         client.send(msg.encode('UTF-8'))
    #         r2 = take_response()
    #         if r2 == 0:
    #             break
    #         else:
    #             if r2.isnumeric():
    #                 bet = round(float(r2),2) # получили ставку от клиента
    #
    #
    #
    #                 pass
    #             else:
    #                 # тут будет сообщение об ошибке ввода
    #                 pass

    else:
        msg = "Некорректный ввод"
        client.send(msg.encode('UTF-8'))