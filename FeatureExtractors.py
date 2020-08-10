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
    def get_number_dict(self, player_hand):
        ret = Util.Counter()
        for card in player_hand:
            ret[card.number] += 1
        return ret

    def get_suit_dict(self, player_hand):
        ret = Util.Counter()
        for card in player_hand:
            ret[card.suit] += 1
        return ret

    def mean_arr(self, arr):
        return sum(card.number for card in arr) / (len(arr) * 14) if len(arr) != 0 else 0

    def get_suit_means(self, player_hand):
        heart_cards = []
        spades_cards = []
        diamonds_cards = []
        clubs_cards = []

        for card in player_hand:
            if card.suit == "hearts":
                heart_cards.append(card)
            elif card.suit == "clubs":
                clubs_cards.append(card)
            elif card.suit == "diamonds":
                diamonds_cards.append(card)
            elif card.suit == "spades":
                spades_cards.append(card)

        heart_cards_mean = self.mean_arr(heart_cards)
        spades_cards_mean = self.mean_arr(spades_cards)
        diamonds_cards_mean = self.mean_arr(diamonds_cards)
        clubs_cards_mean = self.mean_arr(clubs_cards)

        return heart_cards_mean, spades_cards_mean, diamonds_cards_mean, clubs_cards_mean

    def getFeatures(self, state, action):
        features = Util.Counter()

        trump_suit = state.trump_card.suit
        player_hand = state.current_player.get_cards()
        amount_cards = len(state.current_player.get_cards())
        suit_dict = self.get_suit_dict(player_hand)

        features["amount_trump"] = sum(1 for card in player_hand if card.suit == trump_suit) / \
                                 amount_cards if amount_cards != 0 else 0

        features["mean_number"] = sum(card.number for card in player_hand) / amount_cards

        features["variance_number"] = sum((features["mean_number"] - card.number) ** 2 for card in player_hand) / \
                                      amount_cards

        variance_mean = sum(suit_dict.values()) / 4
        features["variance_suit"] = sum((variance_mean - num_suit) ** 2 for num_suit in suit_dict.values()) / 4

        features["cards_diff"] = (len(state.current_player.get_opponent(state).get_cards()) -
                                  len(state.current_player.get_cards())) / 36
        features["is_card_minimum"] = 1 if action == choose_min_card(state.current_player.options(state.table,
                                                                                                  state.trump_card.suit),
                                                                     state.trump_card.suit) else 0

        if len(state.deck.get_cards()) < 6:
            features["cards_on_hand"] = -amount_cards / (36 * (len(state.deck.get_cards()) + 1))

        if len(state.deck.get_cards()) == 0:
            opponent_hand = state.current_player.get_opponent(state).get_cards()
            self_suit_means = self.get_suit_means(player_hand)
            opponent_suit_means = self.get_suit_means(opponent_hand)

            features["amount_trump_opponent"] = -sum(1 for card in opponent_hand if card.suit == trump_suit) / \
                                                len(opponent_hand) if len(opponent_hand) != 0 else 0

            hearts_mean_diff = self_suit_means[0] - opponent_suit_means[0]
            spades_mean_diff = self_suit_means[1] - opponent_suit_means[1]
            diamnods_mean_diff = self_suit_means[2] - opponent_suit_means[2]
            clubs_mean_diff = self_suit_means[3] - opponent_suit_means[3]
            features["suits_means_diff"] = (hearts_mean_diff + spades_mean_diff + diamnods_mean_diff + clubs_mean_diff) / 4

            self_trumps = [card.number for card in player_hand if card.suit == trump_suit]
            enemy_trumps = [card.number for card in opponent_hand if card.suit == trump_suit]
            highest_self_trump = max(self_trumps) if len(self_trumps) != 0 else 0
            highest_enemy_trump = max(enemy_trumps) if len(enemy_trumps) != 0 else 0

            features["highest_trump"] = 1 if highest_self_trump > highest_enemy_trump else -1

        return features
