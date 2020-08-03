import random
import sys
import time
from enum import Enum
from copy import deepcopy

# TODO:
'''
1. Add encoding legend +
2. Add Human player class +
3. Display trumps and cards left in deck in the begining of the round
4. Add ability to pick different Ai playstyles +
5. Encode cards back +
(6. Add way to collect data)
(7. Imporve game visualization)
(8. Make pygame version of a game)
'''


# fix Ai grab option
# fix Player commands during attack\defence

class Card:
    def __init__(self, number, suit):
        self.number = number
        self.suit = suit

    def __repr__(self):
        return str(self.number) + " of " + self.suit

    def __eq__(self, other):
        if other is None:
            return False
        return self.suit == other.suit and self.number == other.number

class Deck:
    def __init__(self):
        self.cards = []
        for i in range(6, 15):
            for suit in ["spades", "hearts", "diamonds", "clubs"]:
                self.cards.append(Card(i, suit))
        random.shuffle(self.cards)
        self.cards.insert(0, self.cards[-1])

    def draw_card(self):
        return self.cards.pop()

    def draw_cards(self, number):
        cards = []
        for _ in range(number):
            cards.append(self.draw_card())
        return cards

# class Deck:
#     '''
#     Class Deck is needed to simulate the card Deck.
#     It has following methods:
#     To initialize Deck instance needed to specify size (36 or 52 cards)
#     '''
#
#     def __init__(self, size):
#         self.size = size
#         self.cards = self.get_deck()
#         self.encoded_cards = DeckEncoder(self).encode()
#         self.encode_legend = DeckEncoder(self).suit_encode()
#
#     def get_deck(self):
#         '''
#         Generates deck
#         '''
#
#         def card_range():
#             try:
#                 if self.size == 52:
#                     card_numbers = [i for i in range(2, 15)]
#                 elif self.size == 36:
#                     card_numbers = [i for i in range(6, 15)]
#                 return card_numbers
#             except UnboundLocalError as card_amount_err:
#                 print("{} Wrong amount of cards".format(card_amount_err))
#                 sys.exit(1)
#
#         def suits():
#             suits_pack_ = ['Diamonds', 'Hearts', 'Spades', 'Clubs']
#             return suits_pack_
#
#         def random_deck():
#             cards = []
#             for number in card_range():
#                 for suit in suits():
#                     cards.append(str(number) + '_' + str(suit))
#                     random.shuffle(cards)
#             return cards
#
#         return random_deck()
#
#     def update_deck(self, num_of_cards):
#         self.encoded_cards = self.encoded_cards[num_of_cards:]
#
#     def show_last_card(self):
#         return self.encoded_cards[-1]


class DeckEncoder:
    '''
    Encoding all str to numerical
    deck_instance == instance of the class Deck
    '''

    def __init__(self, deck_instance):
        self.deck_instance = deck_instance
        self.encode_legend = self.suit_encode()

    def suit_encode(self):
        suits = [(i.split('_')[1]) for i in self.deck_instance.cards]
        trump = suits[-1]
        suits_except_trump = list(set(suits))
        suits_except_trump.remove(trump)
        encode_dict = {trump: 0}
        encode_dict.update(dict([(val, num + 1) for num, val in enumerate(suits_except_trump)]))
        # self.deck_instance.encode_legend = encode_dict
        return encode_dict

    def encode(self):
        splitted_deck = [(i.split('_')) for i in self.deck_instance.cards]
        for num, card in enumerate(splitted_deck):
            splitted_deck[num][0] = int(splitted_deck[num][0])
            splitted_deck[num][1] = self.encode_legend[card[1]]
        # self.deck_instance.encoded_cards = splitted_deck
        return splitted_deck


class DeckDecoder:
    '''
    Encoding all numerical back to str
    '''

    def __init__(self, deck_instance):
        self.deck_instance = deck_instance

    def decode(self):
        encode_legend_rev = dict([[v, k] for k, v in self.deck_instance.encode_legend.items()])
        decoded_deck = [str(i[0]) + '_' + str(encode_legend_rev[i[1]]) \
                        for i in self.deck_instance.encoded_cards]
        self.deck_instance.cards = decoded_deck

    def example(self):
        return ('input:\n{}\noutput:\n{}'.format(self.deck_instance.encoded_cards, self.deck_instance.cards))


class Table:
    def __init__(self):
        self.cards = []

    def update_table(self, card):
        self.cards += [card]

    def move_to_pile(self):
        pass

    def show(self):
        return self.cards

    def clear(self):
        self.cards = []


class Pile:

    def __init__(self):
        self.pile = []

    def update(self, table_instance):
        self.pile += table_instance.cards

    def clear_pile(self):
        self.pile = []

    def show(self):
        return self.pile


class Pointer:
    def __init__(self, list_of_player_instances, trump_suit):
        self.list_of_player_instances = list_of_player_instances
        self.trump_suit = trump_suit
        self._move_pointer_condition = self._init_move_pointer()
        self.attacker_id = self._move_pointer_condition[0]
        self.defender_id = self._move_pointer_condition[1]
        assert self.attacker_id != self.defender_id

    def _init_move_pointer(self):
        start_dict = {}
        for the_player in self.list_of_player_instances:
            try:
                start_dict[the_player] = min([i.number for i in the_player.cards if i.suit == self.trump_suit])
            except ValueError:
                print(ValueError)
        try:
            attacker = min(start_dict, key=start_dict.get)
        except ValueError:  # no trumps for all players
            attacker = (random.choice(self.list_of_player_instances))

        # determination of attacker and defender
        attacker_index = self.list_of_player_instances.index(attacker)
        if len(self.list_of_player_instances) - 1 == attacker_index:
            defender_index = 0
            return (attacker_index, defender_index)
        defender_index = attacker_index + 1
        return (attacker_index, defender_index)

    def switch(self):  # useless?
        self.attacker_id = (self.attacker_id + 1) % 2
        self.defender_id = (self.defender_id + 1) % 2

    def show(self):
        return (self.attacker_id, self.defender_id)


class Round:
    def __init__(self, players_list, pointer, deck, pile, trump_card, table=None, status=None):
        self.players_list = players_list
        self.pointer = pointer
        self.deck = deck
        self.trump_card = trump_card
        self.attacker = players_list[pointer.attacker_id]
        self.attacker.attacking = True
        self.defender = players_list[pointer.defender_id]
        self.table = Table() if table is None else table
        self.pile = pile
        self.status = None if status is None else status
        self.current_player = self.attacker
        self.count = 0

    def round(self):
        if self.check_cards():
            print(self.status)
            return self.status
        if self._first_stage() == True:
            return "first_stage_finish"
        self._second_stage()

    def check_cards(self):
        if self.deck.cards:
            pass
        else:
            return self.check_winner()

        return None

    def check_winner(self):
        winners = []
        if not self.attacker.cards:
            winners.append(self.attacker.nickname)
        if not self.defender.cards:
            winners.append(self.defender.nickname)
        if winners:
            if len(winners) == 2:
                self.status = 'Draw'
                return 'DRAW'
            else:
                self.status = winners[0]
                return self.status

        return None

    def get_next_state_given_card(self, card):
        if self.count >= 7:
            self.pile.update(self.table)
            self.table.clear()
            self.current_player = self.defender
            self.attacker, self.defender = self.defender, self.attacker
            self.attacker.attacking, self.defender.attacking = True, False
            self.attacker.draw_cards(self.deck)
            self.defender.draw_cards(self.deck)
            self.count = 0
            return self

        if card is None:
            if self.defender == self.current_player:
                self.current_player.grab_table()
                self.attacker, self.defender = self.defender, self.attacker
                self.current_player.attacking, self.defender.attacking = \
                    True, False
            else:
                self.current_player = self.defender
                self.attacker, self.defender = self.defender, self.attacker
                self.attacker.attacking, self.defender.attacking = \
                    True, False
                self.pile.update(self.table)
                self.table.clear()
        else:
            self.table.update_table(card)
            # self.current_player.remove_card(card)
            self.current_player.draw_cards(self.deck)

            if self.defender == self.current_player:
                self.current_player = self.attacker
                self.current_player.attacking, self.defender.attacking = \
                    True, False
            else:
                self.defender.attacking = True
                self.current_player = self.defender
                self.current_player.attacking = False

        self.count += 1
        return self

    def _first_stage(self):
        print('atk', len(self.attacker.cards))
        print('def', len(self.defender.cards))
        print('deck', len(self.deck.cards))
        self.current_player = self.attacker
        self.current_player.attacking = True
        self.attacker.attack(self)

        # defender can't defend
        self.current_player = self.defender
        self.current_player.attacking = False
        if self.defender.defend(self) is None:
            print('_first_stage no options for defender')
            self.attacker.draw_cards(self.deck)
            return True
        # defender defended successfully
        return False

    def _second_stage(self):
        cnt = 1
        while True and cnt < 6:
            self.current_player = self.attacker
            self.current_player.attacking = True
            if self.attacker.adding_card(self) is not None:
                cnt += 1
                print('_second_stage no options for defender')
                self.attacker.draw_cards(self.deck)
                return False
            else:
                print('_second_stage no options for attacker')
                self.attacker.draw_cards(self.deck)
                self.defender.draw_cards(self.deck)
                self.pile.update(self.table)
                self.table.clear()
                self.attacker, self.defender = self.defender, self.attacker
                self.attacker.attacking, self.defender.attacking = True, False
                return False
        print('second_stage no cards')

    def copy(self):
        return deepcopy(self)


class GameProcess:
    def __init__(self, players_list, deck):
        self.players_list = players_list
        self.deck = deck
        self.draw_card_for_trump()
        self.get_cards()
        self.pointer = Pointer(players_list, self.trump_card.suit)
        self.table = Table()
        self.pile = Pile()

    def draw_card_for_trump(self):
        self.trump_card = self.deck.draw_card()

    def _refresh_game(self):
        for p in self.players_list:
            p._refresh()

    def get_cards(self):
        for player in self.players_list:
            player.draw_cards(self.deck)

    def get_initial_round(self):
        return Round(self.players_list, self.pointer, self.deck, self.pile, self.trump_card)

    def play(self):
        r = self.get_initial_round()
        i = 0
        while r.status is None:
            print('\n')
            print("round {}".format(i))
            r.round()
            i += 1
        return r.status
