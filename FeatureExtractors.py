# FeatureExtractors.py
# --------------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html


import Util
from Player import choose_min_card


class FeatureExtractor:
    def getFeatures(self, state, action):
        """
          Returns a dict from features to counts
          Usually, the count will just be 1.0 for
          indicator functions.
        """
        Util.raiseNotDefined()


class IdentityExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        features = Util.Counter()
        features[(state, action)] = 1.0
        return features


class LightWeightState:
    def __init__(self, player_hand, table_cards, pile_cards, trump_suit):
        self.over_ten_reg_cards = \
            [card.number for card in player_hand if
             card.suit != trump_suit and card.number > 10]
        self.over_ten_trump_cards = \
            [card.number for card in player_hand if
             card.suit == trump_suit and card.number > 10]

        self.over_ten_reg_cards_in_pile = \
            [card.number for card in pile_cards if
             card.suit != trump_suit and card.number > 10]
        self.over_ten_trump_cards_in_pile = \
            [card.number for card in pile_cards if
             card.suit == trump_suit and card.number > 10]

        self.table_cards = table_cards

        self.amnt_trump = \
            sum(1 for card in player_hand if card.suit == trump_suit)
        self.amnt_non_trump = \
            sum(1 for card in player_hand if card.suit != trump_suit)

    def __repr__(self):
        return "{},{},{},{},{},{},{}".\
            format(self.over_ten_reg_cards,
                   self.over_ten_trump_cards,
                   self.over_ten_reg_cards_in_pile,
                   self.over_ten_trump_cards_in_pile,
                   self.table_cards, self.amnt_trump, self.amnt_non_trump)

    def __hash__(self):
        return hash(repr(self))


class DurakFeatureExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        features = Util.Counter()
        stateFeatures = LightWeightState(state.current_player.cards,
                                         state.table.sort_cards(),
                                         state.pile.sort_cards(),
                                         state.trump_card.suit)
        # feats["over_ten_reg_cards"] = roundFeatures.over_ten_reg_cards / 12
        # feats["over_ten_trump_cards"] = roundFeatures.over_ten_trump_cards / 4
        # feats["num_cards_in_pile"] = len(round.pile.get_cards()) / 36
        # feats["table_cards"] = roundFeatures.table_cards / 12
        amount_cards = len(state.current_player.get_opponent(state).get_cards())
        features[
            "amnt_trump"] = stateFeatures.amnt_trump / amount_cards if \
            amount_cards != 0 else 0
        # feats["amnt_non_trump"] = roundFeatures.amnt_non_trump / 27
        # feats["amnt_cards"] = -len(round.current_player.get_opponent(round).
        # get_cards()) /

        features["cards_diff"] = (len(
            state.current_player.get_opponent(state).get_cards()) -
                               len(state.current_player.get_cards())) / 36
        features["is_card_minimum"] = 1 if action == choose_min_card(
            state.current_player.options(state.table,
                                         state.trump_card.suit),
            state.trump_card.suit) else 0
        return features
