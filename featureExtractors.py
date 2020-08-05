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
        self.over_ten_reg_cards = [card.number for card in player_hand if card.suit != trump_suit and
                                   card.number > 10]
        self.over_ten_trump_cards = [card.number for card in player_hand if card.suit == trump_suit and
                                     card.number > 10]

        self.over_ten_reg_cards_in_pile = [card.number for card in pile_cards if card.suit != trump_suit and
                                           card.number > 10]
        self.over_ten_trump_cards_in_pile = [card.number for card in pile_cards if card.suit == trump_suit and
                                             card.number > 10]

        self.table_cards = table_cards

        self.amnt_trump = sum(1 for card in player_hand if card.suit == trump_suit)
        self.amnt_non_trump = sum(1 for card in player_hand if card.suit != trump_suit)

    def __repr__(self):
        return "{},{},{},{},{},{},{}".format(self.over_ten_reg_cards, self.over_ten_trump_cards,
                                             self.over_ten_reg_cards_in_pile, self.over_ten_trump_cards_in_pile,
                                             self.table_cards, self.amnt_trump, self.amnt_non_trump)

    def __hash__(self):
        return hash(repr(self))


class DurakFeatueExtractor(FeatureExtractor):
    def getFeatures(self, round, action):
        feats = util.Counter()
        roundFeatures = LightWeightState(round.current_player.cards, round.table.sort_cards(), round.pile.sort_cards(),
                                         round.trump_card.suit)
        feats[(roundFeatures, action)] = 1.0
        return feats
