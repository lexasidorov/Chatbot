from random import shuffle




class Deck():
    def __init__(self,cards = None):
        self.__cards = cards

    def create_deck(self):
        values = ["Т", "К", "Д", "В", 10, 9, 8, 7, 6, 5, 4, 3, 2]
        suits = ["♦", "♥", "♧", "♤"]
        cards = [{"suit": x, "value": y} for x in suits for y in values]  # генерим список словарей-карт.
        shuffle(cards)  # тасуем список карт
        self.__cards = cards

    @property
    def cards(self):
        return self.__cards
    @cards.setter
    def cards(self,new_cards):
        if type(new_cards) == list:
            self.__cards = new_cards
        else:
            raise TypeError(f'Value must be list, not {type(new_cards).__name__}')

    def pop_card(self):
        return self.__cards.pop(0)

    def __str__(self):
        new_string = ''
        for item in self.__cards:
            new_string += str(item['value']) + str(item['suit']) + ' '
        return f'Карты: {new_string}'

class Hand(Deck):
    def __init__(self,cards=None,bet=0):
        super().__init__(cards)
        # self.__cards = []
        self.__bet = bet

    @property
    def bet(self):
        return self.__bet
    @bet.setter
    def bet(self,new_bet):
        if type(new_bet) == int or float:
            try:
                self.__bet = int(new_bet)
            except:
                self.__bet = float(new_bet)
        else:
            raise TypeError(f'Value must be int or float, not {type(new_bet).__name__}')

    # @property
    # def cards(self):
    #     return self.__cards
    # @cards.setter
    # def cards(self,new_cards):
    #     self.__cards = new_cards

    def add_card(self,deck):
        if isinstance(deck, Deck):
            if self.cards == None:
                self.cards = list()
            card = deck.pop_card()
            self.cards.append(card)
        else:
            raise TypeError(f'Value must be Deck class, not {type(deck).__name__}')

    def is_splitable(self):
        if len(self.cards) == 2 and self.cards[0]['value'] == self.cards[1]['value']:
            return True
        else:
            return False

    def is_first_ace(self):
        if self.cards[0]['value'] == 'Т':
            return True
        else:
            return False

    def find_score(self):
        score = 0  # сумма очков на руке
        ace_counter = 0  # кол-во тузов в руке
        for card in self.cards:
            if card["value"] in ("К", "Д", "В"):
                score += 10
            elif card["value"] == "Т":
                score += 11
                ace_counter += 1
            else:
                score += card["value"]
        while True:  # если перебор, то туз может быть пересчитан на 1 очко вместо 11
            if score >= 22 and ace_counter >= 1:
                score -= 10
                ace_counter -= 1
            else:
                break
        return score

    def __str__(self):
        new_string = ''
        try:
            for item in self.cards:
                new_string += str(item['value']) + str(item['suit'])+" "
            new_string += f"\tОчки: {self.find_score()}"
        except:
            pass
        # if self.__bet != 0:
        #     new_string += f'\tСтавка {self.__bet}'
        return new_string

class Player():
    def __init__(self, bank=0, hand=None, second_hand=None):
        self.__bank = bank
        self.__hand = hand
        self.__second_hand = second_hand

    def create_player(self):
        self.__hand = Hand()


    def split(self):
        self.__hand.bet /= 2
        self.__second_hand = Hand(bet = self.__hand.bet)
        self.__second_hand.cards = [self.__hand.cards[1]]
        self.__hand.cards.pop()

    def clear(self):
        try:
            self.__hand.cards.clear()
            self.__hand.bet = 0
            self.__second_hand.cards.clear()
            self.__second_hand.bet = 0
        except:
            pass

    @property
    def hand(self):
        return self.__hand
    @hand.setter
    def hand(self,hand):
        if isinstance(hand, Hand):
            self.__hand = hand
        else:
            raise TypeError(f'Value must be Hand class, not {type(hand).__name__}')

    @property
    def second_hand(self):
        return self.__second_hand
    @second_hand.setter
    def second_hand(self, second_hand):
        if isinstance(second_hand, Hand):
            self.__second_hand = second_hand
        else:
            raise TypeError(f'Value must be Hand class, not {type(second_hand).__name__}')

    @property
    def bank(self):
        return self.__bank
    @bank.setter
    def bank(self,bank):
        try:
            self.__bank = bank
        except:
            raise TypeError(f'Value must be int or float, , not {type(bank).__name__}')

    def __str__(self):
        return f'Ваш баланс равен {self.bank}'