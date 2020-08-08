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
        return state.check_win()

    def get_possible_cards(self, state):
        return state.current_player.options(state.table,
                                            state.trump_card.suit)

    def generate_successor(self, state, card):
        copied_state = state.copy()
        return copied_state.get_next_state(card)
