import random
from copy import deepcopy


class Card:
    def __init__(self, number, suit):
        self.number = number
        self.suit = suit

    def __repr__(self):
        return str(self.number) + " of " + self.suit

    def __lt__(self, other):
        return self.__repr__() < other.__repr__()

    def __eq__(self, other):
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

    def get_trump(self):
        return self.cards[0]

    def draw_single_card(self):
        return self.cards.pop()

    def draw_cards(self, number):
        cards = []
        for _ in range(number):
            cards.append(self.draw_single_card())
        return cards


class Table(CardsHolder):
    def __init__(self, cards):
        super().__init__(cards)

    def add_single_card(self, card):
        self.cards.append(card)


class Pile(CardsHolder):

    def __init__(self, cards):
        super().__init__(cards)

    def update(self, table_instance):
        self.add_cards(table_instance.get_cards())


class Pointer:
    def __init__(self, list_of_player_instances, trump_suit):
        self.list_of_player_instances = list_of_player_instances
        self.trump_suit = trump_suit
        self._move_pointer_condition = self._init_move_pointer()
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


class CompressedState:
    def __init__(self, state):
        self.isAttacking = state.current_player.attacking
        self.playerCards = set(state.current_player.sort_cards())
        self.pile = set(state.pile.sort_cards())
        self.table = set(state.table.sort_cards())

    def __repr__(self):
        return '{}#{}#{}#{}'.format(self.isAttacking, self.playerCards,
                                    self.pile, self.table)

    def __eq__(self, other):
        return self.playerCards == other.playerCards and \
               self.table == other.table and self.pile == other.pile and \
               self.isAttacking == other.isAttacking

    def __hash__(self):
        return hash(repr(self))


class State:
    def __init__(self, players_list, pointer, deck, trump_card,
                 pile=None, table=None, status=None):
        self.players_list = players_list
        self.pointer = pointer
        self.deck = deck
        self.trump_card = trump_card
        self.attacker = players_list[pointer.attacker_id]
        self.attacker.attacking = True
        self.current_player = self.attacker
        self.defender = players_list[pointer.defender_id]
        self.table = table if table is not None else Table([])
        self.pile = pile if pile is not None else Pile([])
        self.count = 0
        self.status = None if status is None else status

    def copy(self):
        return deepcopy(self)

    def get_first_stage_attack(self):
        self.current_player = self.attacker
        self.current_player.attacking = True
        self.defender.attacking = False
        self.count += 1
        self.attacker.attack(self)


    def get_second_stage_attack(self):
        self.current_player = self.attacker
        self.current_player.attacking = True
        return self.attacker.add_card(self)

    def get_defence(self):
        self.current_player = self.defender
        self.current_player.attacking = False
        self.count += 1
        return self.defender.defend(self)

    def draw_cards(self):
        self.attacker.draw_cards(self.deck)
        self.defender.draw_cards(self.deck)

    def next_current_player(self):
        if self.current_player == self.attacker:
            self.current_player = self.defender
        else:
            self.current_player = self.attacker

    def swap_players(self):
        self.attacker, self.defender = self.defender, self.attacker
        self.attacker.attacking, self.defender.attacking = True, False

    def prepare_next_state(self):
        self.pile.update(self.table)
        self.table.clear_cards()
        self.draw_cards()
        self.swap_players()
        self.count = 0

    def get_compressed(self):
        return CompressedState(self)

    def play_helper(self):
        if self.check_win():
            print(self.status)
            return self.status
        if self.first_stage():
            # If the defender surrenders, we don't go to the
            # the second stage, but begin a new state
            print("The defender has surrendered")
            return
        # If the defender fought back then we go to the second stage where
        # the attacker can keep attacking
        self.second_stage()

    def check_win(self):
        if self.deck.get_cards():
            return
        else:
            return self.check_winner() is not None

    def check_winner(self):
        winners = []
        if not self.attacker.get_cards():
            winners.append(self.attacker.nickname)
        if not self.defender.get_cards() or \
                (len(self.defender.options(
                    self.table, self.trump_card.suit)) == 1
                 and len(self.defender.get_cards()) == 1):
            winners.append(self.defender.nickname)
        if winners:
            if len(winners) == 2:
                self.status = 'Draw'
                return 'DRAW'
            else:
                self.status = winners[0]
                return 'WIN'

    def get_next_state(self, card):
        if self.count > 12:
            self.current_player = self.defender
            self.prepare_next_state()
            self.count = 0
            return self
        if card is None:
            if self.current_player == self.defender:
                self.current_player.grab_table(self.table)
                self.current_player = self.attacker
            else:
                self.current_player = self.defender
                self.prepare_next_state()
        else:
            self.table.add_single_card(card)
            self.current_player.remove_card(card)
            self.next_current_player()
            self.count += 1
        return self

    def print_first_stage_log(self):
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

    def first_stage(self):
        self.print_first_stage_log()
        self.get_first_stage_attack()
        defence_card = self.get_defence()

        if defence_card is None:
            self.attacker.draw_cards(self.deck)
            return True
        # defender defended successfully
        return False

    def second_stage(self):
        print('\n***Second Stage Begins***\n')
        cnt = 1
        while True and cnt < 6:
            attack_card = self.get_second_stage_attack()
            if attack_card is not None:
                cnt += 1
                defence_card = self.get_defence()
                if defence_card is None:
                    # The defender surrendered
                    self.draw_cards()
                    print("The defender has surrendered")
                    return
            else:
                print("{} doesn't add anymore cards".format(
                    self.attacker.nickname), '\nmoving to the next state!')
                self.prepare_next_state()
                return
        print("No more attacking allowed, moving to the next state!")
        self.prepare_next_state()


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

    def refresh_game(self):
        for p in self.players_list:
            p.clear_cards()

    def get_cards(self):
        for player in self.players_list:
            player.draw_cards(self.deck)

    def get_initial_state(self):
        return State(self.players_list, self.pointer, self.deck,
                     self.trump_card, self.pile, self.table)
    # (self, players_list, pointer, deck, trump_card,
    #                  pile=None, table=None, status=None):

    def play(self):
        current_state = self.get_initial_state()
        i = 0
        while current_state.status is None:
            print('\n')
            print("state {}".format(i))
            current_state.play_helper()
            i += 1
        return current_state.status
