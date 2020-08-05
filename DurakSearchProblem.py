from search import *
from game_mechanics import Deck, GameProcess, Pile
# from gui import RoundWithAI


def diff(l1, l2):
    return [item for item in l1 if item not in l2]


class DurakSearchProblem(SearchProblem):
    def __init__(self, player_list, player_nickname):
        self.player_list = player_list
        self.player_nickname = player_nickname
        self.deck = Deck([])
        # self.possible_cards = self.deck.get_cards()
        #  TODO: This row was used to determine the opponent's cards, but we
        #   can do it directly from the opponent, so this row can be erased
        self.trump_card = None

        self.expanded = 0

    def get_start_state(self):
        for player in self.player_list:
            player._refresh()
        deck = Deck([])

        game_process = GameProcess(self.player_list, deck)
        self.trump_card = game_process.trump_card

        return game_process.get_initial_round()

    def is_goal_state(self, round):
        return round.check_cards() == self.player_nickname

    def is_game_over(self, round):
        return round.check_win() is not None

    def get_cost_of_actions(self, cards_played):
        # Maybe add price if card played was trump card
        return sum([card.number for card in cards_played])

    def get_possible_cards(self, round):
        return round.current_player.options(round.table,
                                            round.trump_card.suit)
        # TODO: Erase the rows commented below?
        # if round.current_player.nickname == self.player_nickname:
        #     return round.current_player.options(round.table,
        #                                        round.trump_card.suit)
        # else:
        #     possible_cards = diff(self.possible_cards, round.pile.pile)
        #     player = next(p for p in self.player_list if p is not round.current_player)
        #     return diff(possible_cards, player.cards)

    def generate_successor(self, round, card):
        copied_round = round.copy()
        return copied_round.get_next_state_given_card(card)

    def get_successors(self, round):
        self.expanded += 1
        if round.current_player.nickname == self.player_nickname:
            possible_cards = set(round.current_player.options(round.table, round.trump_card.suit))
        else:
            #  TODO: We don't need the rows commented below because we can
            #   get the opponent's options directly
            # possible_cards = diff(self.possible_cards,
            #                       round.current_player.get_cards())
            player = next(p for p in self.player_list if p is not round.current_player)
            # possible_cards = diff(possible_cards, player.get_cards())
            possible_cards = player.options(round.table, round.trumpcard.suit)

        next_possible_rounds = []

        for card in possible_cards:
            copied_round = round.copy()
            next_possible_rounds.append(copied_round.get_next_state_given_card(card))

        if len(round.table.playerCards) != 0:
            copied_round = round.copy()
            next_possible_rounds.append(copied_round.get_next_state_given_card(None))

        return next_possible_rounds

# TODO: Erase the rows below?
# class DurakSearchProblemNonGui(DurakSearchProblem):
#     def get_start_state(self):
#         for player in self.player_list:
#             player._refresh()
#         deck = Deck()
#
#         game_process = GameProcess(self.player_list, deck)
#         self.trump_card = game_process.trump_card
#
#         return game_process.get_initial_round()
#
#
# class DurakSearchProblemGui(DurakSearchProblem):
#     def get_start_state(self):
#         for player in self.player_list:
#             player._refresh()
#         deck = Deck()
#         pile = Pile()
#
#         round = RoundWithAI(self.player_list, deck, pile)
#         self.trump_card = round.trump_card
#
#         return round
