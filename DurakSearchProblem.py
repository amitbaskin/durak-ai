from search import *
from game_mechanics import Deck, GameProcess, Pile
from gui import RoundWithAI
from Agents import *


class DurakSearchProblem(SearchProblem):
    def __init__(self, player_list, player_nickname):
        self.player_list = player_list
        self.player_nickname = player_nickname
        deck = Deck()
        self.possible_cards = set(deck.cards)
        self.trump_card = None

        self.expanded = 0

    def get_start_state(self):
        for player in self.player_list:
            player._refresh()
        deck = Deck()

        game_process = GameProcess(self.player_list, deck)
        self.trump_card = game_process.trump_card

        return game_process.get_initial_round()

    def is_goal_state(self, round):
        return round.check_cards() == self.player_nickname

    def is_game_over(self, round):
        return round.check_cards() is not None

    def get_cost_of_actions(self, cards_played):
        # Maybe add price if card played was trump card
        return sum([card.number for card in cards_played])

    def get_possible_cards(self, round):
        if round.current_player.nickname == self.player_nickname:
            return set(round.current_player.options(round.table,
                                               round.trump_card.suit))
        else:
            possible_cards = self.possible_cards.difference(set(round.pile.cards))
            player = next(p for p in self.player_list if p is not round.current_player)
            return possible_cards.difference(set(player.cards))

    def generate_successor(self, round, card):
        copied_round = round.copy()
        return copied_round.get_next_state_given_card(card)

    def get_successors(self, round):
        self.expanded += 1
        if round.current_player.nickname == self.player_nickname:
            possible_cards = set(round.current_player.options(round.table, round.trump_card.suit))
        else:
            possible_cards = self.possible_cards.difference(set(round.pile.cards))
            player = next(p for p in self.player_list if p is not round.current_player)
            possible_cards = possible_cards.difference(set(player.cards))

        next_possible_rounds = []

        for card in possible_cards:
            copied_round = round.copy()
            next_possible_rounds.append(copied_round.get_next_state_given_card(card))

        if len(round.table.cards) != 0:
            copied_round = round.copy()
            next_possible_rounds.append(copied_round.get_next_state_given_card(None))

        return next_possible_rounds


class DurakSearchProblemNonGui(DurakSearchProblem):
    def get_start_state(self):
        for player in self.player_list:
            player._refresh()
        deck = Deck()

        game_process = GameProcess(self.player_list, deck)
        self.trump_card = game_process.trump_card

        return game_process.get_initial_round()


class DurakSearchProblemGui(DurakSearchProblem):
    def get_start_state(self):
        for player in self.player_list:
            player._refresh()
        deck = Deck()
        pile = Pile()

        round = RoundWithAI(self.player_list, deck, pile)
        self.trump_card = round.trump_card

        return round
