import random
from Player import Player, choose_min_card
from MinmaxAgent import MiniMaxAgent
import numpy as np
from qlearningAgents import QlearningAgent, ApproximateQAgent
from DurakSearchProblem import DurakSearchProblem


class DumbPlayer(Player):
    def __init__(self):
        self.nickname = "Random Player"
        super().__init__(self.nickname, [])

    def attack(self, state):
        possible_cards = self.get_attack_options(state.table)
        if len(possible_cards) == 0:
            return None
        attack_card = random.choice(possible_cards)
        return self.attack_helper(attack_card, state)

    def defend(self, state):
        if self.get_defence_options(state.table, state.trump_card.suit):
            defence_card = random.choice(self.get_defence_options(
                state.table, state.trump_card.suit))
            return self.defence_helper(defence_card, state)
        self.no_defence(state)

    def add_card(self, state):
        if self.adding_card_options(state.table):
            card_to_add = random.choice(self.adding_card_options(state.table))
            return self.add_card_helper(card_to_add, state)
        self.no_cards_msg(state)


class SimplePlayer(Player):
    def __init__(self):
        self.nickname = "Simple Player"
        super().__init__(self.nickname, [])

    def attack(self, state):
        possible_cards = self.get_attack_options(state.table)
        if len(possible_cards) == 0:
            return None
        attack_card = choose_min_card(possible_cards, state.trump_card.suit)
        return self.attack_helper(attack_card, state)

    def defend(self, state):
        possible_cards = self.get_defence_options(state.table,
                                                  state.trump_card.suit)
        if possible_cards:
            defence_card = choose_min_card(possible_cards,
                                           state.trump_card.suit)
            return self.defence_helper(defence_card, state)
        self.no_defence(state)

    def add_card(self, state):
        possible_cards = self.adding_card_options(state.table)
        if possible_cards:
            card_to_add = choose_min_card(possible_cards, state.trump_card.suit)
            return self.add_card_helper(card_to_add, state)
        self.no_cards_msg(state)


class HandicapSimplePlayer(Player):
    def __init__(self):
        self.nickname = "Handicapped Simple Player"
        super().__init__(self.nickname, [])

    def attack(self, state):
        if len(state.deck.playerCards) == 0:
            possible_cards = self.get_attack_options(state.table)
            if len(possible_cards) == 0:
                return None
            attack_card = random.choice(possible_cards)
            return self.attack_helper(attack_card, state)
        possible_cards = self.get_attack_options(state.table)
        if len(possible_cards) == 0:
            return None
        attack_card = choose_min_card(possible_cards, state.trump_card.suit)
        return self.attack_helper(attack_card, state)

    def defend(self, state):
        possible_cards = self.get_defence_options(state.table,
                                                  state.trump_card.suit)
        if len(state.deck.playerCards) == 0:
            if possible_cards:
                defence_card = random.choice(self.get_defence_options(
                     state.table, state.trump_card.suit))
                return self.defence_helper(defence_card, state)
            self.no_defence(state)
        if possible_cards:
            defence_card = choose_min_card(possible_cards,
                                           state.trump_card.suit)
            return self.defence_helper(defence_card, state)
        self.no_defence(state)

    def add_card(self, state):
        if len(state.deck.playerCards) == 0:
            if self.adding_card_options(state.table):
                card_to_add = random.choice(
                    self.adding_card_options(state.table))
                return self.add_card_helper(card_to_add, state)
            self.no_cards_msg(state)
        possible_cards = self.adding_card_options(state.table)
        if possible_cards:
            card_to_add = choose_min_card(possible_cards, state.trump_card.suit)
            return self.add_card_helper(card_to_add, state)
        self.no_cards_msg(state)


class SimpleMinmaxPlayer(Player):
    def __init__(self, opponent, name):
        self.nickname = "Smart Player" + name
        super().__init__(self.nickname, [])
        self.minmax_agent = MiniMaxAgent(self.state_evaluation, [self, opponent],
                                         self.nickname)

    def state_evaluation(self, state):
        my_cards_amount = len(self.get_cards())
        opponent_cards = self.get_opponent(state).get_cards()
        opponent_cards_amount = len(opponent_cards)
        if my_cards_amount == 0 and opponent_cards_amount > 0:
            return np.inf
        return len(opponent_cards) - len(self.get_cards())

    def attack(self, state):
        possible_cards = self.get_attack_options(state.table)
        if len(state.deck.get_cards()) == 0:
            if len(possible_cards) == 0:
                return None
            attack_card = self.minmax_agent.get_card_to_play(state)
            if attack_card is None:
                attack_card = choose_min_card(
                    possible_cards, state.trump_card.suit)
            return self.attack_helper(attack_card, state)

        if len(possible_cards) == 0:
            return None
        attack_card = choose_min_card(possible_cards, state.trump_card.suit)

        return self.attack_helper(attack_card, state)

    def defend(self, state):
        if len(state.deck.get_cards()) == 0:
            possible_cards = self.get_defence_options(
                state.table, state.trump_card.suit)
            if possible_cards:
                defence_card = self.minmax_agent.get_card_to_play(state)
                if defence_card is not None:
                    return self.defence_helper(defence_card, state)
            return self.no_defence(state)

        possible_cards = self.get_defence_options(state.table,
                                                  state.trump_card.suit)
        if possible_cards:
            defence_card = choose_min_card(possible_cards,
                                           state.trump_card.suit)
            return self.defence_helper(defence_card, state)
        self.no_defence(state)

    def add_card(self, state):
        if len(state.deck.get_cards()) == 0:
            possible_cards = self.adding_card_options(state.table)
            if possible_cards:
                card_to_add = self.minmax_agent.get_card_to_play(state)
                if card_to_add is not None:
                    self.add_card_helper(card_to_add, state)

            self.no_cards_msg(state)

        possible_cards = self.adding_card_options(state.table)
        if possible_cards:
            card_to_add = choose_min_card(possible_cards, state.trump_card.suit)

            return self.add_card_helper(card_to_add, state)

        self.no_cards_msg(state)


class QlearningMinmaxPlayer(Player):
    def __init__(self, opponent, name):
        self.nickname = "Smart Player" + name
        super().__init__(self.nickname, [])
        self.minmax_agent = MiniMaxAgent(self.state_evaluation,
                                         [self, opponent], self.nickname)
        self.q_agent = QlearningAgent(
            self.minmax_agent.searcher.get_possible_cards, numTraining=50)

    def state_evaluation(self, state):
        my_cards_amount = len(self.get_cards())
        opponent_cards = self.get_opponent(state).get_cards()
        opponent_cards_amount = len(opponent_cards)
        if my_cards_amount == 0 and opponent_cards_amount > 0:
            return np.inf
        return len(opponent_cards) - len(self.get_cards())

    def attack(self, state):
        possible_cards = self.get_attack_options(state.table)
        if len(state.deck.cards) == 0:
            if len(possible_cards) == 0:
                return None
            attack_card = self.minmax_agent.get_card_to_play(state)
            if attack_card is None:
                attack_card = choose_min_card(
                    possible_cards, state.trump_card.suit)

            return self.attack_helper(attack_card, state)

        if len(possible_cards) == 0:
            return None
        attack_card = self.q_agent.getAction(state.copy())
        if attack_card is None:
            attack_card = choose_min_card(possible_cards, state.trump_card.suit)

        return self.attack_helper(attack_card, state)

    def defend(self, state):
        possible_cards = self.get_defence_options(state.table,
                                                  state.trump_card.suit)
        if len(state.deck.cards) == 0:
            if possible_cards:
                defence_card = self.minmax_agent.get_card_to_play(state)
                if defence_card is None:
                    defence_card = choose_min_card(possible_cards,
                                                   state.trump_card.suit)
                if defence_card is not None:
                    return self.defence_helper(defence_card, state)
            self.no_defence(state)

        return self.q_learning_defence(possible_cards, state)

    def add_card(self, state):
        possible_cards = self.adding_card_options(state.table)
        if len(state.deck.cards) == 0:
            if possible_cards:
                return self.add_card_minimax(possible_cards, state)

            self.no_cards_msg(state)

        return self.add_card_q_learning(possible_cards, state)


class PureQlearningPlayer(Player):
    def __init__(self, opponent, name, approx=True):
        self.nickname = "Smart Player" + name
        super().__init__(self.nickname, [])
        self.searcher = DurakSearchProblem([self, opponent], self.nickname)
        self.q_agent = ApproximateQAgent(
            self.searcher.get_possible_cards) if approx else \
            QlearningAgent(self.searcher.get_possible_cards)

    def get_opponent(self, state):
        if self.nickname == state.attacker.nickname:
            return state.defender
        return state.attacker


    def attack(self, state):
        possible_cards = self.get_attack_options(state.table)

        if len(possible_cards) == 0:
            return None
        attack_card = self.q_agent.getAction(state.copy())
        if attack_card is None:
            attack_card = choose_min_card(possible_cards, state.trump_card.suit)

        return self.attack_helper(attack_card, state)

    def defend(self, state):
        possible_cards = self.get_defence_options(state.table,
                                                  state.trump_card.suit)

        return self.q_learning_defence(possible_cards, state)

    def add_card(self, state):
        possible_cards = self.adding_card_options(state.table)

        return self.add_card_q_learning(possible_cards, state)
