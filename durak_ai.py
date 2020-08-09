import random
from player import Player
from Agents import MiniMaxAgent
import numpy as np
from qlearningAgents import DurakQAgent, ApproximateQAgent
from DurakSearchProblem import DurakSearchProblem

NO_CARDS_MSG = 'has no cards to add'
FEATURING_TABLE_MSG = 'table: '
ADDING_CARD_MSG = 'adds'
NO_DEFENCE_MSG = "can't defend"
DEFENCE_MSG = 'defends with'
ATTACK_MSG = 'attacks with'


def choose_min_card(possible_cards, trump_suit):
    trump_cards = [card for card in possible_cards if card.suit == trump_suit]
    non_trump_cards = [card for card in possible_cards if card.suit !=
                       trump_suit]
    non_trump_cards.sort(key=lambda x: x.number)
    if len(non_trump_cards) == 0:
        trump_cards.sort(key=lambda x: x.number)
        return trump_cards[0]
    return non_trump_cards[0]


class AiPlayerDumb(Player):
    def __init__(self):
        self.nickname = "Random Player"
        super().__init__(self.nickname, [])

    def attack(self, round):
        possible_cards = self.attacking_options(round.table)
        if len(possible_cards) == 0:
            return None
        attack_card = random.choice(possible_cards)
        return self.attack_helper(attack_card, round)

    def defend(self, round):
        if self.defending_options(round.table, round.trump_card.suit):
            defence_card = random.choice(self.defending_options(
                round.table, round.trump_card.suit))
            return self.defence_helper(defence_card, round)
        self.no_defence(round)

    def adding_card(self, round):
        if self.adding_card_options(round.table):
            card_to_add = random.choice(self.adding_card_options(round.table))
            return self.add_card_helper(card_to_add, round)
        self.no_cards_msg(round)


class SimplePlayer(Player):
    def __init__(self):
        self.nickname = "Simple Player"
        super().__init__(self.nickname, [])

    def attack(self, round):
        possible_cards = self.attacking_options(round.table)
        if len(possible_cards) == 0:
            return None
        attack_card = choose_min_card(possible_cards, round.trump_card.suit)
        return self.attack_helper(attack_card, round)

    def defend(self, round):
        possible_cards = self.defending_options(round.table,
                                                round.trump_card.suit)
        if possible_cards:
            defence_card = choose_min_card(possible_cards,
                                           round.trump_card.suit)
            return self.defence_helper(defence_card, round)
        self.no_defence(round)

    def adding_card(self, round):
        possible_cards = self.adding_card_options(round.table)
        if possible_cards:
            card_to_add = choose_min_card(possible_cards, round.trump_card.suit)
            return self.add_card_helper(card_to_add, round)
        self.no_cards_msg(round)


class HandicappedSimplePlayer(Player):
    def __init__(self):
        self.nickname = "Handicapped Simple Player"
        super().__init__(self.nickname, [])

    def attack(self, round):
        if len(round.deck.playerCards) == 0:
            possible_cards = self.attacking_options(round.table)
            if len(possible_cards) == 0:
                return None
            attack_card = random.choice(possible_cards)
            return self.attack_helper(attack_card, round)
        possible_cards = self.attacking_options(round.table)
        if len(possible_cards) == 0:
            return None
        attack_card = choose_min_card(possible_cards, round.trump_card.suit)
        return self.attack_helper(attack_card, round)

    def defend(self, round):
        possible_cards = self.defending_options(round.table,
                                                round.trump_card.suit)
        if len(round.deck.playerCards) == 0:
            if possible_cards:
                defence_card = random.choice(self.defending_options(
                    round.table, round.trump_card.suit))
                return self.defence_helper(defence_card, round)
            self.no_defence(round)
        if possible_cards:
            defence_card = choose_min_card(possible_cards,
                                           round.trump_card.suit)
            return self.defence_helper(defence_card, round)
        self.no_defence(round)

    def adding_card(self, round):
        if len(round.deck.playerCards) == 0:
            if self.adding_card_options(round.table):
                card_to_add = random.choice(self.adding_card_options(round.table))
                return self.add_card_helper(card_to_add, round)
            self.no_cards_msg(round)
        possible_cards = self.adding_card_options(round.table)
        if possible_cards:
            card_to_add = choose_min_card(possible_cards, round.trump_card.suit)
            return self.add_card_helper(card_to_add, round)
        self.no_cards_msg(round)


class SmartPlayer(Player):
    def __init__(self, opponent, name, depth=5):
        self.nickname = "Smart Player" + name
        super().__init__(self.nickname, [])
        self.agent = MiniMaxAgent(self.round_evaluation, [self, opponent],
                                  self.nickname, depth=depth)

    def get_opponent(self, round):
        if self.nickname == round.attacker.nickname:
            return round.defender
        return round.attacker

    # def round_evaluation(self, round):
    #     me = round.attacker if self.attacking else round.defender
    #
    #     my_cards_amount = len(me.get_cards())
    #     opponent_cards = self.get_opponent(round).get_cards()
    #     opponent_cards_amount = len(opponent_cards)
    #     if my_cards_amount == 0 and opponent_cards_amount > 0:
    #         return np.inf
    #
    #     if opponent_cards_amount == 0:
    #         return -np.inf
    #
    #     ret = opponent_cards_amount - my_cards_amount
    #     return ret

    def round_evaluation(self, round):
        me = round.attacker if self.attacking else round.defender

        my_cards_amount = len(me.get_cards())
        opponent_cards = self.get_opponent(round).get_cards()
        opponent_cards_amount = len(opponent_cards)
        if my_cards_amount == 0 and opponent_cards_amount > 0:
            return np.inf

        if opponent_cards_amount == 0:
            return -np.inf

        # ret = sum(card.number for card in me.get_cards()) / my_cards_amount - \
        #       sum(card.number for card in self.get_opponent(round).get_cards()) / opponent_cards_amount + \
        ret = (opponent_cards_amount - my_cards_amount)# * 5
        return ret

    def attack(self, round):
        possible_cards = self.attacking_options(round.table)
        if len(round.deck.get_cards()) == 0:
            if len(possible_cards) == 0:
                return None
            attack_card = self.agent.get_card_to_play(round)
            if attack_card is None:
                attack_card = choose_min_card(possible_cards, round.trump_card.suit)
            return self.attack_helper(attack_card, round)

        if len(possible_cards) == 0:
            return None
        attack_card = choose_min_card(possible_cards, round.trump_card.suit)

        return self.attack_helper(attack_card, round)

    def defend(self, round):
        if len(round.deck.get_cards()) == 0:
            possible_cards = self.defending_options(round.table, round.trump_card.suit)
            if possible_cards:
                defence_card = self.agent.get_card_to_play(round)
                if defence_card is not None:
                    return self.defence_helper(defence_card, round)
            return self.no_defence(round)

        possible_cards = self.defending_options(round.table,
                                                round.trump_card.suit)
        if possible_cards:
            defence_card = choose_min_card(possible_cards,
                                           round.trump_card.suit)
            return self.defence_helper(defence_card, round)
        self.no_defence(round)

    def adding_card(self, round):
        if len(round.deck.get_cards()) == 0:
            possible_cards = self.adding_card_options(round.table)
            if possible_cards:
                card_to_add = self.agent.get_card_to_play(round)
                if card_to_add is not None:
                    self.add_card_helper(card_to_add, round)

            self.no_cards_msg(round)

        possible_cards = self.adding_card_options(round.table)
        if possible_cards:
            card_to_add = choose_min_card(possible_cards, round.trump_card.suit)

            return self.add_card_helper(card_to_add, round)

        self.no_cards_msg(round)


class PureQAgent(Player):
    def __init__(self, opponent, name, approx=True, for_train=True):
        self.nickname = "Smart Player" + name
        super().__init__(self.nickname, [])
        self.searcher = DurakSearchProblem([self, opponent], self.nickname)
        if for_train:
            self.qAgent = ApproximateQAgent(self.searcher.get_possible_cards) if approx else \
                DurakQAgent(self.searcher.get_possible_cards)
        else:
            self.qAgent = ApproximateQAgent(self.searcher.get_possible_cards, epsilon=0, gamma=0, alpha=0) if approx \
                else DurakQAgent(self.searcher.get_possible_cards)

    def get_opponent(self, round):
        if self.nickname == round.attacker.nickname:
            return round.defender
        return round.attacker

    def attack(self, round):
        possible_cards = self.attacking_options(round.table)

        if len(possible_cards) == 0:
            return None
        attack_card = self.qAgent.getAction(round.copy())
        if attack_card is None:
            attack_card = choose_min_card(possible_cards, round.trump_card.suit)

        return self.attack_helper(attack_card, round)

    def defend(self, round):
        possible_cards = self.defending_options(round.table,
                                                round.trump_card.suit)

        return self.q_learning_defence(possible_cards, round)

    def adding_card(self, round):
        possible_cards = self.adding_card_options(round.table)

        return self.add_card_q_learning(possible_cards, round)
