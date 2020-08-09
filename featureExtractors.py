# featureExtractors.py
# --------------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

"Feature extractors for Pacman game states"

# from game import Directions, Actions
import util
import numpy as np


class FeatureExtractor:
    def getFeatures(self, state, action):
        """
          Returns a dict from features to counts
          Usually, the count will just be 1.0 for
          indicator functions.
        """
        util.raiseNotDefined()


class IdentityExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        feats = util.Counter()
        feats[(state, action)] = 1.0
        return feats


class LightWeightState:
    def __init__(self, player_hand, table_cards, pile_cards, trump_suit):
        self.over_ten_reg_cards = len([card.number for card in player_hand if card.suit != trump_suit and
                                   card.number > 10])
        self.over_ten_trump_cards = len([card.number for card in player_hand if card.suit == trump_suit and
                                     card.number > 10])

        self.over_ten_reg_cards_in_pile = len([card.number for card in pile_cards if card.suit != trump_suit and
                                           card.number > 10])
        self.over_ten_trump_cards_in_pile = len([card.number for card in pile_cards if card.suit == trump_suit and
                                             card.number > 10])

        self.table_cards = len(table_cards)

        self.amnt_trump = sum(1 for card in player_hand if card.suit == trump_suit)
        self.amnt_non_trump = sum(1 for card in player_hand if card.suit != trump_suit)

    def __repr__(self):
        return "{},{},{},{},{},{},{}".format(self.over_ten_reg_cards, self.over_ten_trump_cards,
                                             self.over_ten_reg_cards_in_pile, self.over_ten_trump_cards_in_pile,
                                             self.table_cards, self.amnt_trump, self.amnt_non_trump)

    def __hash__(self):
        return hash(repr(self))

def choose_min_card(possible_cards, trump_suit):
    trump_cards = [card for card in possible_cards if card.suit == trump_suit]
    non_trump_cards = [card for card in possible_cards if card.suit !=
                       trump_suit]
    non_trump_cards.sort(key=lambda x: x.number)
    if len(non_trump_cards) == 0:
        if len(trump_cards) == 0:
            return None
        trump_cards.sort(key=lambda x: x.number)
        return trump_cards[0]
    return non_trump_cards[0]

class DurakFeatueExtractor(FeatureExtractor):
    # def getFeatures(self, round, action):
    #     feats = util.Counter()
    #     roundFeatures = LightWeightState(round.current_player.cards, round.table.sort_cards(), round.pile.sort_cards(),
    #                                      round.trump_card.suit)
    #     feats[(roundFeatures, action)] = 1.0
    #     return feats

    def getFeatures(self, round, action):
        feats = util.Counter()
        roundFeatures = LightWeightState(round.current_player.cards, round.table.sort_cards(), round.pile.sort_cards(),
                                         round.trump_card.suit)
        # feats["over_ten_reg_cards"] = roundFeatures.over_ten_reg_cards / 12
        # feats["over_ten_trump_cards"] = roundFeatures.over_ten_trump_cards / 4
        # feats["num_cards_in_pile"] = len(round.pile.get_cards()) / 36
        # feats["table_cards"] = roundFeatures.table_cards / 12
        amount_cards = len(round.current_player.get_opponent(round).get_cards())
        feats["amnt_trump"] = roundFeatures.amnt_trump / amount_cards if amount_cards != 0 else 0
        # feats["amnt_non_trump"] = roundFeatures.amnt_non_trump / 27
        # feats["amnt_cards"] = -len(round.current_player.get_opponent(round).get_cards()) /

        feats["cards_diff"] = (len(round.current_player.get_opponent(round).get_cards()) -
                               len(round.current_player.get_cards())) / 36
        feats["is_card_minimum"] = 1 if action == choose_min_card(round.current_player.options(round.table,
                                                                                               round.trump_card.suit),
                                                                  round.trump_card.suit) else 0
        return feats
