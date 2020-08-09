# QlearningAgents.py
# ------------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html


import os
import pickle
import random
import Util
import numpy as np

from FeatureExtractors import DurakFeatureExtractor
from LearningAgents import ReinforcementAgent


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
        self.q_values = Util.Counter()

    def getQValue(self, compressed_state, action):
        """
          Returns Q(state,action)
          Should return 0.0 if we never seen
          a state or (state,action) tuple
        """
        compressed_state = compressed_state.get_compressed()
        ret = self.q_values[(compressed_state, action)]
        remove_zero_items(self.q_values)
        return ret

    def getValue(self, state):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        possible_actions = self.getLegalActions(state)
        values = dict()
        for action in possible_actions:
            values[action] = self.getQValue(state, action)

        return max(values.values()) if len(values) != 0 else 0.0

    def getPolicy(self, state):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        possible_actions = self.getLegalActions(state)
        values = dict()
        for action in possible_actions:
            values[action] = self.getQValue(state, action)

        max_actions = []
        max_value = -np.inf
        for action, value in values.items():
            if value >= max_value:
                if max_value != value:
                    max_actions.clear()
                max_actions.append(action)
                max_value = value
        return random.choice(max_actions) if len(max_actions) != 0 else None

    def getAction(self, state):
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.

          HINT: You might want to use util.flipCoin(prob)
          HINT: To pick randomly from a list, use random.choice(list)
        """
        legalActions = self.getLegalActions(state)
        if len(legalActions) == 0:
            return None
        if Util.flipCoin(self.epsilon):
            return random.choice(legalActions)
        else:
            return self.getPolicy(state)

    def update(self, compressed_state, action, nextstate, reward):
        """
          The parent class calls this to observe a
          state = action => nextState and reward transition.
          You should do your Q-Value update here

          NOTE: You should never call this function,
          it will be called on your behalf
        """
        values = []
        for next_action in self.getLegalActions(nextstate):
            next_state_compressed = nextstate.get_compressed()
            values.append(self.q_values[(next_state_compressed, next_action)])
        max_value = max(values) if len(values) != 0 else 0
        compressed_state = compressed_state.get_compressed()
        coefficient = reward + self.discount * max_value - \
                      self.q_values[(compressed_state, action)]
        add = self.alpha * coefficient
        if add != 0:
            self.q_values[(compressed_state, action)] += add


class DurakQAgent(QLearningAgent):
    def __init__(self, legalActions_ptr, 
                 epsilon=0.05, gamma=0.8, alpha=0.2, numTraining=0):
        """
        These default parameters can be changed from the pacman.py command line.
        For example, to change the exploration rate, try:
            python pacman.py -p PacmanQLearningAgent -a epsilon=0.1

        alpha    - learning rate
        epsilon  - exploration rate
        gamma    - discount factor
        numTraining -
        number of training episodes, i.e. no learning after these many episodes
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

        if os.path.isfile(os.path.join("qValues",
                                       "trained_q_values_latest.pickle")):
            with open(os.path.join("qValues", "trained_q_values_latest.pickle"),
                      'rb') as handle:
                self.q_values = Util.Counter(pickle.load(handle))

        self.getLegalActions = legalActions_ptr


def remove_zero_items(weights):
    return Util.Counter(dict(filter(lambda x: x[1] != 0, weights.items())))


class ApproximateQAgent(DurakQAgent):
    """
       ApproximateQLearningAgent

       You should only have to overwrite getQValue
       and update.  All other QLearningAgent functions
       should work as is.
    """

    def __init__(self, legalActions_ptr, epsilon=0.05, gamma=0.8, alpha=0.2,
                 numTraining=0, **args):
        self.featExtractor = DurakFeatureExtractor()
        DurakQAgent.__init__(self, legalActions_ptr, epsilon=0.05, gamma=0.4, alpha=0.08, **args)

        # You might want to initialize weights here.
        self.weights = Util.Counter()

        if os.path.isfile(os.path.join("pickle", 
                                       "trained_weights_latest.pickle")):
            with open(os.path.join("pickle", "trained_weights_latest.pickle"), 
                      'rb') as handle:
                self.weights = Util.Counter(pickle.load(handle))

    def getQValue(self, state, action):
        """
          Should return Q(state,action) = w * featureVector
          where * is the dotProduct operator
        """
        features = self.featExtractor.getFeatures(state, action)
        ret = self.weights * features
        # self.weights = remove_zero_items(self.weights)
        return ret

    def update(self, state, action, next_state, reward):
        """
           Should update your weights based on transition
        """
        values = []
        for next_action in self.getLegalActions(next_state):
            values.append(self.getQValue(next_state, next_action))
        max_value = max(values) if len(values) != 0 else 0
        correction = reward + self.discount * max_value - \
                     self.getQValue(state, action)
        features = self.featExtractor.getFeatures(state, action)
        for feature, value in features.items():
            w = self.alpha * correction * value
            self.weights[feature] += w
