import random
from player import Player
from Agents import MiniMaxAgent
import numpy as np
from qlearningAgents import DurakQAgent


def diff(l1, l2):
    return [item for item in l1 if item not in l2]


class AiPlayerDumb(Player):
    def __init__(self):
        self.nickname = "Random Player"
        super().__init__(self.nickname)

    def attack(self, round):
        possible_cards = self.attacking_options(round.table)
        if len(possible_cards) == 0:
            return None
        attack_card = random.choice(possible_cards)
        self.remove_card(attack_card)
        round.table.update_table(attack_card)
        print('{} attack with {} of {}'.format(self.nickname, attack_card.number, attack_card.suit))
        return attack_card

    def defend(self, round):
        if self.defending_options(round.table, round.trump_card.suit):
            defence_card = random.choice(self.defending_options(round.table, round.trump_card.suit))
            self.remove_card(defence_card)
            round.table.update_table(defence_card)
            print('{} defended with {}'.format(self.nickname, defence_card))
            return defence_card
        print(r"{} can't defend".format(self.nickname))
        print('table:', round.table.show())
        self.grab_table(round.table)
        return None

    def adding_card(self, round):
        if self.adding_card_options(round.table):
            card_to_add = random.choice(self.adding_card_options(round.table))
            self.remove_card(card_to_add)
            round.table.update_table(card_to_add)
            print('{} adding card {}'.format(self.nickname, card_to_add))
            #print('T add: {}'.format(table.show()))
            return card_to_add
        print('{} no cards to add'.format(self.nickname))
        print('table: {}'.format(round.table.show()))
        return None


def choose_min_card(possible_cards, trump_suit):
    trump_cards = [card for card in possible_cards if card.suit == trump_suit]
    non_trump_cards = [card for card in possible_cards if card.suit != trump_suit]

    non_trump_cards.sort(key=lambda x: x.number)

    if len(non_trump_cards) == 0:
        trump_cards.sort(key=lambda x: x.number)
        return trump_cards[0]

    return non_trump_cards[0]


class SimplePlayer(Player):
    def __init__(self):
        self.nickname = "Simple Player"
        super().__init__(self.nickname)

    def attack(self, round):
        possible_cards = self.attacking_options(round.table)
        if len(possible_cards) == 0:
            return None
        attack_card = choose_min_card(possible_cards, round.trump_card.suit)
        self.remove_card(attack_card)
        round.table.update_table(attack_card)
        print('{} attack with {} of {}'.format(self.nickname, attack_card.number, attack_card.suit))
        return attack_card

    def defend(self, round):
        possible_cards = self.defending_options(round.table, round.trump_card.suit)
        if possible_cards:
            defence_card = choose_min_card(possible_cards, round.trump_card.suit)
            self.remove_card(defence_card)
            round.table.update_table(defence_card)
            print('{} defended with {}'.format(self.nickname, defence_card))
            return defence_card
        print(r"{} can't defend".format(self.nickname))
        print('table:', round.table.show())
        self.grab_table(round.table)
        return None

    def adding_card(self, round):
        possible_cards = self.adding_card_options(round.table)
        if possible_cards:
            card_to_add = choose_min_card(possible_cards, round.trump_card.suit)
            self.remove_card(card_to_add)
            round.table.update_table(card_to_add)
            print('{} adding card {}'.format(self.nickname, card_to_add))
            #print('T add: {}'.format(table.show()))
            return card_to_add
        print('{} no cards to add'.format(self.nickname))
        print('table: {}'.format(round.table.show()))
        return None


class HandicappedSimplePlayer(Player):
    def __init__(self):
        self.nickname = "Handicapped Simple Player"
        super().__init__(self.nickname)

    def attack(self, round):
        if len(round.deck.playerCards) == 0:
            possible_cards = self.attacking_options(round.table)
            if len(possible_cards) == 0:
                return None
            attack_card = random.choice(possible_cards)
            self.remove_card(attack_card)
            round.table.update_table(attack_card)
            print('{} attack with {} of {}'.format(self.nickname, attack_card.number, attack_card.suit))
            return attack_card

        possible_cards = self.attacking_options(round.table)
        if len(possible_cards) == 0:
            return None
        attack_card = choose_min_card(possible_cards, round.trump_card.suit)
        self.remove_card(attack_card)
        round.table.update_table(attack_card)
        print('{} attack with {} of {}'.format(self.nickname, attack_card.number, attack_card.suit))
        return attack_card

    def defend(self, round):
        if len(round.deck.playerCards) == 0:
            if self.defending_options(round.table, round.trump_card.suit):
                defence_card = random.choice(self.defending_options(round.table, round.trump_card.suit))
                self.remove_card(defence_card)
                round.table.update_table(defence_card)
                print('{} defended with {}'.format(self.nickname, defence_card))
                return defence_card
            print(r"{} can't defend".format(self.nickname))
            print('table:', round.table.show())
            self.grab_table(round.table)
            return None

        possible_cards = self.defending_options(round.table, round.trump_card.suit)
        if possible_cards:
            defence_card = choose_min_card(possible_cards, round.trump_card.suit)
            self.remove_card(defence_card)
            round.table.update_table(defence_card)
            print('{} defended with {}'.format(self.nickname, defence_card))
            return defence_card
        print(r"{} can't defend".format(self.nickname))
        print('table:', round.table.show())
        self.grab_table(round.table)
        return None

    def adding_card(self, round):
        if len(round.deck.playerCards) == 0:
            if self.adding_card_options(round.table):
                card_to_add = random.choice(self.adding_card_options(round.table))
                self.remove_card(card_to_add)
                round.table.update_table(card_to_add)
                print('{} adding card {}'.format(self.nickname, card_to_add))
                #print('T add: {}'.format(table.show()))
                return card_to_add
            print('{} no cards to add'.format(self.nickname))
            print('table: {}'.format(round.table.show()))
            return None

        possible_cards = self.adding_card_options(round.table)
        if possible_cards:
            card_to_add = choose_min_card(possible_cards, round.trump_card.suit)
            self.remove_card(card_to_add)
            round.table.update_table(card_to_add)
            print('{} adding card {}'.format(self.nickname, card_to_add))
            #print('T add: {}'.format(table.show()))
            return card_to_add
        print('{} no cards to add'.format(self.nickname))
        print('table: {}'.format(round.table.show()))
        return None


class SmartPlayer(Player):
    def __init__(self, opponent, name):
        self.nickname = "Smart Player" + name
        super().__init__(self.nickname)
        self.agent = MiniMaxAgent(self.round_evaluation, [self, opponent],
                                  self.nickname)


    def get_opponent(self, round):
        if self.nickname == round.attacker.nickname:
            return round.defender
        return round.attacker

    def round_evaluation(self, round):
        my_cards_amount = len(self.cards)
        opponent_cards = self.get_opponent(round).cards
        opponent_cards_amount = len(opponent_cards)
        if my_cards_amount == 0 and opponent_cards_amount > 0:
            return np.inf
        return len(opponent_cards) - len(self.cards) #diff(opponent_cards, self.cards))

    def attack(self, round):
        possible_cards = self.attacking_options(round.table)
        if len(round.deck.cards) == 0:
            if len(possible_cards) == 0:
                return None
            attack_card = self.agent.get_card_to_play(round)
            if attack_card is None:
                attack_card = choose_min_card(possible_cards, round.trump_card.suit)
            self.remove_card(attack_card)
            round.table.update_table(attack_card)
            print('{} attack with {} of {}'.format(self.nickname, attack_card.number, attack_card.suit))
            return attack_card

        if len(possible_cards) == 0:
            return None
        attack_card = choose_min_card(possible_cards, round.trump_card.suit)
        self.remove_card(attack_card)
        round.table.update_table(attack_card)
        print(
            '{} attack with {} of {}'.format(self.nickname, attack_card.number,
                                             attack_card.suit))
        return attack_card

    def defend(self, round):
        if len(round.deck.cards) == 0:
            possible_cards = self.defending_options(round.table, round.trump_card.suit)
            if possible_cards:
                defence_card = self.agent.get_card_to_play(round)
                if defence_card is not None:
                    print(defence_card)
                    self.remove_card(defence_card)
                    round.table.update_table(defence_card)
                    print('{} defended with {}'.format(self.nickname, defence_card))
                return defence_card
            print(r"{} can't defend".format(self.nickname))
            print('table:', round.table.show())
            self.grab_table(round.table)
            return None

        possible_cards = self.defending_options(round.table,
                                                round.trump_card.suit)
        if possible_cards:
            defence_card = choose_min_card(possible_cards,
                                           round.trump_card.suit)
            self.remove_card(defence_card)
            round.table.update_table(defence_card)
            print('{} defended with {}'.format(self.nickname, defence_card))
            return defence_card
        print(r"{} can't defend".format(self.nickname))
        print('table:', round.table.show())
        self.grab_table(round.table)
        return None

    def adding_card(self, round):
        if len(round.deck.cards) == 0:
            possible_cards = self.adding_card_options(round.table)
            if possible_cards:
                card_to_add = self.agent.get_card_to_play(round)
                if card_to_add is not None:
                    self.remove_card(card_to_add)
                    round.table.update_table(card_to_add)
                    print('{} adding card {}'.format(self.nickname, card_to_add))
                #print('T add: {}'.format(table.show()))
                return card_to_add
            print('{} no cards to add'.format(self.nickname))
            print('table: {}'.format(round.table.show()))
            return None

        possible_cards = self.adding_card_options(round.table)
        if possible_cards:
            card_to_add = choose_min_card(possible_cards, round.trump_card.suit)
            self.remove_card(card_to_add)
            round.table.update_table(card_to_add)
            print('{} adding card {}'.format(self.nickname, card_to_add))
            #print('T add: {}'.format(table.show()))
            return card_to_add
        print('{} no cards to add'.format(self.nickname))
        print('table: {}'.format(round.table.show()))
        return None


class SmartPlayer2(Player):
    def __init__(self, opponent, name):
        self.nickname = "Smart Player" + name
        super().__init__(self.nickname)
        self.minMaxAgent = MiniMaxAgent(self.round_evaluation, [self, opponent],
                                        self.nickname)
        self.qAgent = DurakQAgent([self, opponent], self.minMaxAgent.searcher.get_possible_cards, numTraining=50)

    def get_opponent(self, round):
        if self.nickname == round.attacker.nickname:
            return round.defender
        return round.attacker

    def round_evaluation(self, round):
        my_cards_amount = len(self.cards)
        opponent_cards = self.get_opponent(round).cards
        opponent_cards_amount = len(opponent_cards)
        if my_cards_amount == 0 and opponent_cards_amount > 0:
            return np.inf
        return len(opponent_cards) - len(self.cards) #diff(opponent_cards, self.cards))

    def attack(self, round):
        possible_cards = self.attacking_options(round.table)
        if len(round.deck.cards) == 0:
            if len(possible_cards) == 0:
                return None
            attack_card = self.minMaxAgent.get_card_to_play(round)
            if attack_card is None:
                attack_card = choose_min_card(possible_cards, round.trump_card.suit)
            self.remove_card(attack_card)
            round.table.update_table(attack_card)
            print('{} attack with {} of {}'.format(self.nickname, attack_card.number, attack_card.suit))
            return attack_card

        if len(possible_cards) == 0:
            return None
        attack_card = self.qAgent.getAction(round.copy())
        if attack_card is None:
            attack_card = choose_min_card(possible_cards, round.trump_card.suit)
        self.remove_card(attack_card)
        round.table.update_table(attack_card)
        print(
            '{} attack with {} of {}'.format(self.nickname, attack_card.number,
                                             attack_card.suit))
        return attack_card

    def defend(self, round):
        if len(round.deck.cards) == 0:
            possible_cards = self.defending_options(round.table, round.trump_card.suit)
            if possible_cards:
                defence_card = self.minMaxAgent.get_card_to_play(round)
                if defence_card is None:
                    defence_card = choose_min_card(possible_cards,
                                                   round.trump_card.suit)
                if defence_card is not None:
                    print(defence_card)
                    self.remove_card(defence_card)
                    round.table.update_table(defence_card)
                    print('{} defended with {}'.format(self.nickname, defence_card))
                    return defence_card
            print(r"{} can't defend".format(self.nickname))
            print('table:', round.table.show())
            self.grab_table(round.table)
            return None

        possible_cards = self.defending_options(round.table,
                                                round.trump_card.suit)
        if possible_cards:
            defence_card = self.qAgent.getAction(round.copy())
            if defence_card is None:
                defence_card = choose_min_card(possible_cards,
                                              round.trump_card.suit)
            self.remove_card(defence_card)
            round.table.update_table(defence_card)
            print('{} defended with {}'.format(self.nickname, defence_card))
            return defence_card
        print(r"{} can't defend".format(self.nickname))
        print('table:', round.table.show())
        self.grab_table(round.table)
        return None

    def adding_card(self, round):
        if len(round.deck.cards) == 0:
            possible_cards = self.adding_card_options(round.table)
            if possible_cards:
                card_to_add = self.minMaxAgent.get_card_to_play(round)
                if card_to_add is None:
                    card_to_add = choose_min_card(possible_cards,
                                                   round.trump_card.suit)
                    self.remove_card(card_to_add)
                    round.table.update_table(card_to_add)
                    print('{} adding card {}'.format(self.nickname, card_to_add))
                #print('T add: {}'.format(table.show()))
                    return card_to_add
            print('{} no cards to add'.format(self.nickname))
            print('table: {}'.format(round.table.show()))
            return None

        possible_cards = self.adding_card_options(round.table)
        if possible_cards:
            card_to_add = self.qAgent.getAction(round.copy())
            if card_to_add is None:
                card_to_add = choose_min_card(possible_cards,
                                              round.trump_card.suit)
            self.remove_card(card_to_add)
            round.table.update_table(card_to_add)
            print('{} adding card {}'.format(self.nickname, card_to_add))
            #print('T add: {}'.format(table.show()))
            return card_to_add
        print('{} no cards to add'.format(self.nickname))
        print('table: {}'.format(round.table.show()))
        return None
