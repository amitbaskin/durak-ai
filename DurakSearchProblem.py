from search import *
from game_mechanics import Deck, GameProcess


class DurakSearchProblem(SearchProblem):
    def __init__(self, player_list, player_nickname):
        self.player_list = player_list
        self.player_nickname = player_nickname
        self.deck = Deck([])
        self.trump_card = None
        self.expanded = 0

    def get_start_state(self):
        for player in self.player_list:
            player.clear_cards()
        deck = Deck([])

        game_process = GameProcess(self.player_list, deck)
        self.trump_card = game_process.trump_card

        return game_process.get_initial_state()

    def is_goal_state(self, state):
        return state.check_cards() == self.player_nickname

    def is_game_over(self, state):
        return state.check_win() is not None

    def get_cost_of_actions(self, cards_played):
        # Maybe add price if card played was trump card
        return sum([card.number for card in cards_played])

    def get_possible_cards(self, state):
        return state.current_player.options(state.table,
                                            state.trump_card.suit)

    def generate_successor(self, state, card):
        copied_state = state.copy()
        return copied_state.get_next_state_given_card(card)

    def get_successors(self, state):
        self.expanded += 1
        if state.current_player.nickname == self.player_nickname:
            possible_cards = set(state.current_player.options(
                state.table, state.trump_card.suit))
        else:
            player = next(
                p for p in self.player_list if p is not state.current_player)
            possible_cards = player.options(state.table, state.trumpcard.suit)

        next_possible_states = []

        for card in possible_cards:
            copied_state = state.deepcopy()
            next_possible_states.append(
                copied_state.get_next_state_given_card(card))

        if len(state.table.playerCards) != 0:
            copied_state = state.deepcopy()
            next_possible_states.append(
                copied_state.get_next_state_given_card(None))

        return next_possible_states
