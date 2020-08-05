import random
# import sys
# import time
# from enum import Enum
from copy import deepcopy
import bisect

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

    def __lt__(self, other):
        return self.__repr__() < other.__repr__()

    def __eq__(self, other):
        # TODO: why do we need to check this?
        if other is None or other == [None]:
            return False
        return self.suit == other.suit and self.number == other.number

    def suit_num_delta(self):
        if self.suit == "spades":
            return 0
        if self.suit == "hearts":
            return 13
        if self.suit == "diamonds":
            return 26
        if self.suit == "clubs":
            return 39

    def __hash__(self):
        return self.number + self.suit_num_delta()


class CardsHolder:
    def __init__(self, cards):
        self.cards = cards

    def get_cards(self):
        return self.cards

    def set_cards(self, cards):
        self.cards = cards

    def add_cards(self, cards):
        for card in cards:
            self.cards.append(card)

    def remove_card(self, card):
        self.cards.remove(card)

    def clear_cards(self):
        self.cards = []

    def sort_cards(self):
        self.cards.sort()
        return self.get_cards()



class Deck(CardsHolder):
    def __init__(self, cards):
        super().__init__(cards)
        for i in range(6, 15):
            for suit in ["spades", "hearts", "diamonds", "clubs"]:
                self.add_cards([Card(i, suit)])
        random.shuffle(self.cards)
        # self.cardsObject.cards.insert(0, self.cardsObject.cards[-1]) #
        # TODO: What is the purpose of this row?

    def get_trump(self):
        return self.cards[0]

    def draw_single_card(self):
        return self.cards.pop()

    def draw_cards(self, number):
        cards = []
        for _ in range(number):
            cards.append(self.draw_single_card())
        return cards



# TODO: Delete This?
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


class Table(CardsHolder):
    def __init__(self, cards):
        super().__init__(cards)

    def add_single_card(self, card):
        self.cards.append(card)

    # TODO: to remove this method?
    def move_to_pile(self):
        pass


class Pile(CardsHolder):

    def __init__(self, cards):
        super().__init__(cards)

    def update(self, table_instance):
        self.add_cards(table_instance.get_cards())


class Pointer:
    def __init__(self, list_of_player_instances, trump_suit):
        self.list_of_player_instances = list_of_player_instances
        self.trump_suit = trump_suit
        self._move_pointer_condition = self._init_move_pointer()  #
        # Determines who should be the attacker first
        self.attacker_id = self._move_pointer_condition[0]
        self.defender_id = self._move_pointer_condition[1]
        assert self.attacker_id != self.defender_id

    def _init_move_pointer(self):
        start_dict = {}
        for the_player in self.list_of_player_instances:
            try:
                start_dict[the_player] = min([i.number for i in
                                              the_player.get_cards() if i.suit
                                              == self.trump_suit])
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



class State:
    def __init__(self, current_player, pile):
        self.current_player = current_player
        self.isAttacking = current_player.attacking
        self.playerCards = current_player.sort_cards()
        self.pile = pile.sort_cards()

    def __str__(self):
        return '{}#{}#{}#{}'.format(self.current_player, self.isAttacking,
                                    self.playerCards, self.pile)


class Round:
    def __init__(self, players_list, pointer, deck, pile, trump_card, table=None, status=None):
        self.players_list = players_list
        self.pointer = pointer
        self.deck = deck
        self.trump_card = trump_card
        self.attacker = players_list[pointer.attacker_id]
        self.attacker.attacking = True
        self.defender = players_list[pointer.defender_id]
        self.table = Table([]) if table is None else table
        self.pile = pile
        self.status = None if status is None else status
        self.current_player = self.attacker
        self.count = 0


    def toState(self):
        return State(self.current_player, self.pile)


    def round(self):
        if self.check_win():
            print(self.status)
            return self.status
        if self._first_stage():
            # If the defender surrenders, we don't go to the
            # the second stage, but begin a new round
            return "first_stage_finish"
        # If the defender fought back then we go to the second stage where
        # the attacker can keep attacking
        self._second_stage()

    def check_win(self):
        if self.deck.get_cards():
            pass
        else:
            return self.check_winner()

        return None

    def check_winner(self):
        winners = []
        if not self.attacker.get_cards():
            winners.append(self.attacker.nickname)
        if not self.defender.get_cards():
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
            self.table.clear_cards()
            self.current_player = self.defender
            self.attacker, self.defender = self.defender, self.attacker
            self.attacker.attacking, self.defender.attacking = True, False
            self.attacker.draw_cards(self.deck)
            self.defender.draw_cards(self.deck)
            self.count = 0
            return self

        if card is None:
            if self.defender == self.current_player:
                self.current_player.grab_table(self.table)
                self.attacker, self.defender = self.defender, self.attacker
                self.current_player.attacking, self.defender.attacking = \
                    True, False
            else:
                self.current_player = self.defender
                self.attacker, self.defender = self.defender, self.attacker
                self.attacker.attacking, self.defender.attacking = \
                    True, False
                self.pile.update(self.table)
                self.table.clear_cards()
        else:
            self.table.add_single_card(card)
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

        print('\n***First Stage Begins***\n')
        print('trump_card: ', self.trump_card)

        attacker_cards = self.attacker.sort_cards()
        print('atk', len(attacker_cards))
        print(attacker_cards)

        defender_cards = self.defender.sort_cards()
        print('def', len(defender_cards))
        print(defender_cards)

        table_cards = self.table.sort_cards()
        print('table', len(table_cards))
        print(table_cards)

        deck_cards = self.deck.sort_cards()
        print('deck', len(deck_cards))
        print(deck_cards)

        pile_cards = self.pile.sort_cards()
        print('pile', len(pile_cards))
        print(pile_cards)

        self.current_player = self.attacker
        self.current_player.attacking = True
        self.defender.attacking = False
        self.attacker.attack(self)
        self.current_player = self.defender
        self.current_player.attacking = False
        if self.defender.defend(self) is None:
            self.attacker.draw_cards(self.deck)
            return True
        # defender defended successfully
        return False

    def _second_stage(self):
        print('\n***Second Stage Begins***\n')
        cnt = 1
        while True and cnt < 6:
            # TODO: In each condition we return something so we don't really
            #  let the loop take place
            self.current_player = self.attacker
            self.current_player.attacking = True
            if self.attacker.adding_card(self) is not None:
                cnt += 1
                #  TODO: Why can't the defender defend? delete this commented
                #   printing below?
                # print('_second_stage no options for defender')
                if self.defender.defend(self) is None:
                    self.attacker.draw_cards(self.deck)
                    # TODO: Delete this! why should attacker keep getting
                    #  cards while the defender doesn't?
                    continue
                # The defender surrendered
                return False
            else:
                print("{} doesn't add anymore cards".format(self.attacker.nickname))
                self.attacker.draw_cards(self.deck)
                self.defender.draw_cards(self.deck)
                self.pile.update(self.table)
                self.table.clear_cards()
                self.attacker, self.defender = self.defender, self.attacker
                self.attacker.attacking, self.defender.attacking = True, False
                return False
        # TODO: what does this printing mean? furthermore, if attacker
        #  attacked six times then the defender should draw cards
        print('second_stage no cards')
        self.defender.draw_cards(self.deck)


    def copy(self):
        return deepcopy(self)


class GameProcess:
    def __init__(self, players_list, deck):
        self.players_list = players_list
        self.deck = deck
        self.trump_card = self.draw_card_for_trump()
        self.get_cards()
        self.pointer = Pointer(players_list, self.trump_card.suit)
        self.table = Table([])
        self.pile = Pile([])

    def draw_card_for_trump(self):
         return self.deck.get_trump()

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


class DeckEncoder:
    '''
    Encoding all str to numerical
    deck_instance == instance of the class Deck
    '''

    def __init__(self, deck_instance):
        self.deck_instance = deck_instance
        self.encode_legend = self.suit_encode()

    def suit_encode(self):
        suits = [(i.split('_')[1]) for i in self.deck_instance.playerCards]
        trump = suits[-1]
        suits_except_trump = list(set(suits))
        suits_except_trump.remove(trump)
        encode_dict = {trump: 0}
        encode_dict.update(dict([(val, num + 1) for num, val in enumerate(suits_except_trump)]))
        # self.deck_instance.encode_legend = encode_dict
        return encode_dict

    def encode(self):
        splitted_deck = [(i.split('_')) for i in self.deck_instance.playerCards]
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
        self.deck_instance.playerCards = decoded_deck

    def example(self):
        return ('input:\n{}\noutput:\n{}'.format(self.deck_instance.encoded_cards, self.deck_instance.playerCards))