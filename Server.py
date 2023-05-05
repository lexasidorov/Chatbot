from socket import *
import time
from urllib.request import urlopen
import requests
from xml.etree import ElementTree as ET
from blackjack import *


def send(msg):
    client.send(msg.encode('UTF-8'))

def take_response():
    response = client.recv(1024)  # получаем данные от клиента
    r = response.decode('UTF-8')
    return r

s = socket(AF_INET,SOCK_STREAM) # создадим объект сокета (сетевой, потоковый)
s.bind(("",8888)) #настраиваем сокет на локальный IP и порт
s.listen(5) #режим ожидания, <=5 запросов одновременно


client,addr = s.accept()    #принимаем запрос на соединение
print(f"Получен запрос на соединение {str(addr)}")

menu = (
    '\n1 - узнать время\t2 - курс доллара\t3 - операции с числами\n4 - рассказать анекдот\t5 - сыграть в Блекджек'
)
hello = 'Привет!' + menu
client.send(hello.encode('UTF-8'))  #отправляем первое сообщение
player = Player()# создаём объект игрока, в нём хранится информация о счёте в игре.
player.create_player()

while True:
    r1 = take_response()
    if r1 == '1':
        timestr = time.ctime(time.time()) + menu   # формируем строку с текущей датой и временем
        client.send(timestr.encode('UTF-8'))
    elif r1 == '2':
        rate_usd = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()    # получаем словарь
        rate_usd_rrf = rate_usd['Valute']['USD']['Value']    # находим значение по ключам
        msg = f'Курс доллара {rate_usd_rrf}' + menu
        send(msg)
    elif r1 == '3':
        msg = 'Введите математическое выражение'
        while True:
            send(msg)
            r2 = take_response()
            try:
                msg = f'{r2} = {eval(r2)}' + menu # вычисляем мат.выражение
                send(msg)
                break
            except:
                msg = "Некорректное выражение. Попробуйте ещё раз."  # возвращаем сообщение об ошибке
                send(msg)
    elif r1 == '4':
        with urlopen('http://rzhunemogu.ru/Rand.aspx?CType=1') as r:
            xml_element = (ET.fromstring(r.read(), ET.XMLParser(encoding='Windows-1251'))) # создаем xml элемент
            for i in xml_element:
                joke = i.text
        msg = joke + '\n' + menu
        send(msg)
    elif r1 == '5':
        player = Player()# создаём игрока и дилера
        player.create_player()
        dealer = Player()
        dealer.create_player()
        stage = 1
        msg = ""
        while True:
            if stage == 0: # выход из игры
                send(menu)
                break
            if stage == 1:
                player.clear()
                dealer.clear()
                deck = Deck() # создаём колоду
                deck.create_deck()
                msg += f"\n{player}. Делайте ставку. Минимальная ставка 10 (0 для выхода в меню)"
                handname = "Ваши карты "
                add_to_msg = ""
                split = False
                ensurance = 0
                while True:
                    send(msg)
                    r2 = take_response()
                    if r2 == '0':
                        stage = 0
                        break
                    elif not r2.isdigit() or int(r2) < 10:
                        msg = 'Такие ставки не принимаются!'
                    else:
                        player.hand.bet = int(r2)
                        stage = 2
                        break
            if stage == 2:
                player.hand.add_card(deck)
                player.hand.add_card(deck)
                dealer.hand.add_card(deck)
                dealer.hand.add_card(deck)
                stage = 3
                # Блекджек при раздаче карт
                if player.hand.find_score() == 21:
                    if dealer.hand.find_score() == 21:
                        msg = f"Ваши карты {player.hand}\tСтавка {player.hand.bet}" \
                              f"\nКарты дилера {dealer.hand}" \
                              f"\nНичья! У вас и у дилера Блекджек."
                    else:
                        player.bank += player.hand.bet*1.5 # Блэкджек оплачивается 3/2
                        msg = f"Ваши карты {player.hand}\tСтавка {player.hand.bet}\n" \
                              f"Карты дилера {dealer.hand}\n" \
                              f"Блекджек! Ваша ставка оплачивается 3/2\n"
                    stage = 1
                # страховая ставка
                elif dealer.hand.is_first_ace():
                    msg = f"Ваши карты {player.hand}\tСтавка {player.hand.bet}\n" \
                          f"Первая карта дилера {str(dealer.hand.cards[0]['value'])+str(dealer.hand.cards[0]['suit'])}\n" \
                          f"Вы можете застраховать ставку. Страховка - это ставка, которая выигрывает, если у дилера Блекджек\n" \
                          f"Размер страховки не может превышать {int(player.hand.bet/2)} и быть менее 5. Введите 0, если хотите отказаться от страховки\n"
                    while True:
                        send(msg)
                        r3 = take_response()
                        if not r3.isdigit():
                            msg = 'Вы ввели не целое число!'
                        elif int(r3) < 0 or int(r3) > int(player.hand.bet/2):
                            msg = 'Такие ставки не принимаются!'
                        elif int(r3) == 0:
                            add_to_msg = 'Вы отказались от страховки\n' # добавим к следующему сообщению
                            break
                        else:
                            ensurance = int(r3)
                            add_to_msg = f"Страховая ставка {ensurance}"
                            break
                if stage == 3:
                    # Сплит
                    if player.hand.is_splitable():
                        msg = f"Ваши карты{player.hand}\tСтавка {player.hand.bet}\n" \
                              f"Вы можете сделать сплит, для этого отправьте \"1\""
                        send(msg)
                        r4 = take_response()
                        if r4 == "1":
                            player.split()
                            split = True
                            handname = "Карты слева "

                    # Первая рука. Ещё карту?
                    active_hand = player.hand
                    take_counter = 0
                    while True:
                        msg = f"Первая карта дилера {str(dealer.hand.cards[0]['value']) + str(dealer.hand.cards[0]['suit'])}\n" \
                              f"{handname}{active_hand}\tСтавка {active_hand.bet}\n" \
                              f"1 - Ещё карту\t2 - Удвоение\t0 - Хватит\n"
                        if active_hand.find_score() > 21:
                            if split and active_hand == player.hand:
                                active_hand = player.second_hand
                                handname = "Карты справа "
                                take_counter = 0
                                msg = "Перебор!\n" \
                                      f"Первая карта дилера {str(dealer.hand.cards[0]['value']) + str(dealer.hand.cards[0]['suit'])}\n" \
                                      f"{handname}{active_hand}\tСтавка {active_hand.bet}\n" \
                                      f"1 - Ещё карту\t2 - Удвоение\t0 - Хватит\n"
                            else:
                                break
                        if take_counter > 0:
                            msg = f"Первая карта дилера {str(dealer.hand.cards[0]['value']) + str(dealer.hand.cards[0]['suit'])}\n" \
                              f"{handname}{active_hand}\tСтавка {active_hand.bet}\n" \
                              f"1 - Ещё карту\t0 - Хватит\n"
                        send(msg)
                        r5 = take_response()
                        if r5 == '1':
                            active_hand.add_card(deck) # Добавили карту
                        elif r5 == '2' and take_counter == 0:
                            active_hand.add_card(deck) # Добавили карту и выходим из цикла
                            active_hand.bet *= 2
                            if split and active_hand == player.hand:
                                active_hand = player.second_hand
                                handname = "Карты справа "
                                take_counter = 0
                            else:
                                break
                        elif r5 == '0':
                            if split and active_hand == player.hand:
                                active_hand = player.second_hand
                                handname = "Карты справа "
                                take_counter = 0
                            else:
                                break
                        else:
                            send("Ошибка ввода. Введите 1, 2 или 0")

                    # Проверка блекджека у дилера
                    if dealer.hand.find_score() == 21 and ensurance != 0:
                        player.bank += ensurance
                        add_to_msg += "выиграла.\n"
                    elif dealer.hand.find_score() != 21 and 0 != ensurance:
                        player.bank -= ensurance
                        add_to_msg += "проиграла.\n"
                    # Дилер набирает карты
                    while True:
                        if dealer.hand.find_score() <= 16:
                            dealer.hand.add_card(deck)
                        else:
                            break
                    # Сравниваем карты дилера и игрока
                    msg = f"Карты дилера {dealer.hand}"
                    if dealer.hand.find_score() > 21:
                        msg += " Перебор!"
                        while True:
                            if active_hand.find_score() <= 21:
                                player.bank += active_hand.bet
                                msg += f"\n{handname} {active_hand}\tСтавка {active_hand.bet} выиграла\n"
                            else:
                                msg += f"\n{handname} {active_hand} Перебор!\tСтавка {active_hand.bet} возвращается\n"
                            if active_hand == player.second_hand:
                                active_hand = player.hand
                            else:
                                break
                    else:
                        while True:
                            if active_hand.find_score() < dealer.hand.find_score():
                                player.bank -= active_hand.bet
                                msg += f"\n{handname} {active_hand}\tСтавка {active_hand.bet} проиграла\n"
                            elif active_hand.find_score() > 21:
                                player.bank -= active_hand.bet
                                msg +=  f"\n{handname} {active_hand} Перебор!\tСтавка {active_hand.bet} проиграла\n"
                            elif active_hand.find_score() > dealer.hand.find_score():
                                player.bank += active_hand.bet
                                msg += f"\n{handname} {active_hand}\tСтавка {active_hand.bet} выиграла\n"
                            else:
                                msg += f"\n{handname} {active_hand}\tСтавка {active_hand.bet} возвращается\n"
                            if active_hand == player.second_hand:
                                active_hand = player.hand
                            else:
                                break
                    stage = 1

    else:
        msg = "Некорректный ввод"
        send(msg)