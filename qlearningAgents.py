# qlearningAgents.py
# ------------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

# from game import *
from learningAgents import ReinforcementAgent
# from featureExtractors import *
# from DurakSearchProblem import DurakSearchProblem

import random, util, math
import pickle
import numpy as np
import os
from featureExtractors import DurakFeatueExtractor


class QLearningAgent(ReinforcementAgent):
    """
      Q-Learning Agent

      Functions you should fill in:
        - getQValue
        - getAction
        - getValue
        - getPolicy
        - update

      Instance variables you have access to
        - self.epsilon (exploration prob)
        - self.alpha (learning rate)
        - self.discount (discount rate)

      Functions you should use
        - self.getLegalActions(state)
          which returns legal actions
          for a state
    """

    def __init__(self, **args):
        "You can initialize Q-values here..."
        ReinforcementAgent.__init__(self, **args)
        self.q_values = util.Counter()

    def getQValue(self, round, action):
        """
          Returns Q(state,action)
          Should return 0.0 if we never seen
          a state or (state,action) tuple
        """
        state = round.toState()
        ret = self.q_values[(state, action)]
        remove_zero_items(self.q_values)
        return ret

    def getValue(self, round):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        possible_actions = self.getLegalActions(round)
        values = dict()
        for action in possible_actions:
            values[action] = self.getQValue(round, action)

        return max(values.values()) if len(values) != 0 else 0.0

    def getPolicy(self, round):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        possible_actions = self.getLegalActions(round)
        values = dict()
        for action in possible_actions:
            values[action] = self.getQValue(round, action)

        max_actions = []
        max_value = -np.inf
        for action, value in values.items():
            if value >= max_value:
                if max_value != value:
                    max_actions.clear()
                max_actions.append(action)
                max_value = value
        return random.choice(max_actions) if len(max_actions) != 0 else None

    def min_action(self, possible_actions, trump_suit):
        trump_cards = [card for card in possible_actions if card.suit == trump_suit]
        non_trump_cards = [card for card in possible_actions if card.suit != trump_suit]
        non_trump_cards.sort(key=lambda x: x.number)
        if len(non_trump_cards) == 0:
            trump_cards.sort(key=lambda x: x.number)
            return trump_cards[0]
        return non_trump_cards[0]

    def getAction(self, round):
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.

          HINT: You might want to use util.flipCoin(prob)
          HINT: To pick randomly from a list, use random.choice(list)
        """
        legalActions = self.getLegalActions(round)
        if len(legalActions) == 0:
            return None
        if util.flipCoin(self.epsilon):
            return random.choice(legalActions)
            # return self.min_action(legalActions, round.trump_card.suit)
        else:
            return self.getPolicy(round)

    def update(self, round, action, nextRound, reward):
        """
          The parent class calls this to observe a
          state = action => nextState and reward transition.
          You should do your Q-Value update here

          NOTE: You should never call this function,
          it will be called on your behalf
        """
        values = []
        for next_action in self.getLegalActions(nextRound):
            nextState = nextRound.toState()
            values.append(self.q_values[(nextState, next_action)])
        max_value = max(values) if len(values) != 0 else 0
        state = round.toState()
        coefficient = reward + self.discount * max_value - self.q_values[(state, action)]
        add = self.alpha * coefficient
        if add != 0:
            self.q_values[(state, action)] += add


class DurakQAgent(QLearningAgent):
    def __init__(self, legalActions_ptr, epsilon=0.05, gamma=0.8, alpha=0.2, numTraining=0):
        """
        These default parameters can be changed from the pacman.py command line.
        For example, to change the exploration rate, try:
            python pacman.py -p PacmanQLearningAgent -a epsilon=0.1

        alpha    - learning rate
        epsilon  - exploration rate
        gamma    - discount factor
        numTraining - number of training episodes, i.e. no learning after these many episodes
        """
        args = dict()
        args['epsilon'] = epsilon
        args['gamma'] = gamma
        args['alpha'] = alpha
        args['numTraining'] = numTraining
        self.episodeRewards = 0
        self.index = 0  # This is always Pacman
        QLearningAgent.__init__(self, **args)
        self.weights = None

        if os.path.isfile(os.path.join("qValues", "trained_q_values_latest.pickle")):
            with open(os.path.join("qValues", "trained_q_values_latest.pickle"), 'rb') as handle:
                self.q_values = util.Counter(pickle.load(handle))

        self.getLegalActions = legalActions_ptr


def remove_zero_items(weights):
    return util.Counter(dict(filter(lambda x: x[1] != 0, weights.items())))


class ApproximateQAgent(DurakQAgent):
    """
       ApproximateQLearningAgent

       You should only have to overwrite getQValue
       and update.  All other QLearningAgent functions
       should work as is.
    """

    def __init__(self, legalActions_ptr, epsilon=0.05, gamma=0.8, alpha=0.2, **args):
        self.featExtractor = DurakFeatueExtractor()
        DurakQAgent.__init__(self, legalActions_ptr, epsilon=0.2, gamma=0.6, alpha=0.7, **args)

        # You might want to initialize weights here.
        self.weights = util.Counter()

        if os.path.isfile(os.path.join("pickle", "trained_weights_latest.pickle")):
            with open(os.path.join("pickle", "trained_weights_latest.pickle"), 'rb') as handle:
                self.weights = util.Counter(pickle.load(handle))

    def getQValue(self, state, action):
        """
          Should return Q(state,action) = w * featureVector
          where * is the dotProduct operator
        """
        features = self.featExtractor.getFeatures(state, action)
        ret = self.weights * features
        # self.weights = remove_zero_items(self.weights)
        return ret

    def update(self, round, action, nextRound, reward):
        """
           Should update your weights based on transition
        """
        values = []
        for next_action in self.getLegalActions(nextRound):
            values.append(self.getQValue(nextRound, next_action))
        max_value = max(values) if len(values) != 0 else 0
        correction = reward + self.discount * max_value - self.getQValue(round, action)
        features = self.featExtractor.getFeatures(round, action)
        for feature, value in features.items():
            w = self.alpha * correction * value
            self.weights[feature] += w
