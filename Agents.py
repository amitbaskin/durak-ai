import abc
import numpy as np
from DurakSearchProblem import DurakSearchProblem


class Agent(object):
    def __init__(self):
        super(Agent, self).__init__()

    @abc.abstractmethod
    def get_card_to_play(self, state):
        return

    def stop_running(self):
        pass


class MultiAgentSearchAgent(Agent):
    def __init__(self, evaluation_function, depth=5):
        super().__init__()
        self.evaluation_function = evaluation_function
        self.depth = depth

    @abc.abstractmethod
    def get_card_to_play(self, state):
        return


class MiniMaxAgent(MultiAgentSearchAgent):
    def __init__(self, evaluation_function, players_list, nickname):
        super().__init__(evaluation_function)
        self.searcher = DurakSearchProblem(players_list, nickname)

    def minimax(self, currentDepth, current_state,  targetDepthToAdd):
        def minimax_algorithm(depth, curr_state, max_turn,
                              target_depth, card_to_play):
            if depth == target_depth:
                return self.evaluation_function(curr_state), card_to_play

            if self.searcher.is_game_over(curr_state):
                return self.evaluation_function(curr_state), card_to_play

            if max_turn:
                possible_states = []
                options = self.searcher.get_possible_cards(curr_state)
                for possible_card in options:
                    state = self.searcher.generate_successor(curr_state, possible_card)
                    if depth == 0 and card_to_play is None:
                        curr_card_to_play = possible_card
                    else:
                        curr_card_to_play = card_to_play

                    possible_states.append(
                        minimax_algorithm(depth + 1, state, False,
                                          target_depth,
                                          curr_card_to_play))
                if len(possible_states) == 0:
                    return -np.inf, card_to_play
                return max(possible_states, key=lambda x: x[0])

            else:
                possible_states = []
                for possible_card in self.searcher.get_possible_cards(curr_state):
                    state = self.searcher.generate_successor(curr_state,
                                                             possible_card)
                    if depth == 0 and card_to_play is None:
                        curr_action = possible_card
                    else:
                        curr_action = card_to_play
                    possible_states.append(
                        minimax_algorithm(depth + 1, state, True,
                                          target_depth,
                                          curr_action))
                if len(possible_states) == 0:
                    return self.evaluation_function(curr_state), card_to_play
                return min(possible_states, key=lambda x: x[0])

        return minimax_algorithm(currentDepth, current_state, True,
                                 currentDepth + targetDepthToAdd * 2, None)[1]

    def alpha_beta_pruning(self, currentDepth, currentstate,
                           targetDepthToAdd):
        def alpha_beta_pruning_algorithm(depth, curr_state, max_turn, target_depth, alpha, beta, card_to_play):
            if depth == target_depth:
                return self.evaluation_function(curr_state), card_to_play

            if self.searcher.is_game_over(curr_state):
                return self.evaluation_function(curr_state), card_to_play

            if max_turn:
                possible_states = []
                max_eval = -np.inf, None
                for possible_card in self.searcher.get_possible_cards(curr_state) + [None]:
                    state = self.searcher.generate_successor(curr_state, possible_card)
                    if depth == 0 and card_to_play is None:
                        curr_action = possible_card
                    else:
                        curr_action = card_to_play
                    curr_eval = alpha_beta_pruning_algorithm(depth + 1, state,
                                                             False,
                                                             target_depth,
                                                             alpha, beta,
                                                             curr_action)
                    possible_states.append(curr_eval)
                    max_eval = max(max_eval, curr_eval, key=lambda x: x[0])
                    alpha = max(alpha, curr_eval[0])
                    if beta <= alpha:
                        break
                if len(possible_states) == 0:
                    return self.evaluation_function(curr_state), card_to_play
                return max(possible_states, key=lambda x: x[0])

            else:
                possible_states = []
                min_eval = np.inf, None
                for possible_card in self.searcher.get_possible_cards(curr_state) + [None]:
                    state = self.searcher.generate_successor(curr_state, possible_card)
                    if depth == 0 and card_to_play is None:
                        curr_action = possible_card
                    else:
                        curr_action = card_to_play
                    curr_eval = alpha_beta_pruning_algorithm(depth + 1, state,
                                                             True,
                                                             target_depth,
                                                             alpha, beta,
                                                             curr_action)
                    possible_states.append(curr_eval)
                    min_eval = min(min_eval, curr_eval, key=lambda x: x[0])
                    beta = min(beta, curr_eval[0])
                    if beta <= alpha:
                        break
                if len(possible_states) == 0:
                    return self.evaluation_function(curr_state), card_to_play
                return min(possible_states, key=lambda x: x[0])

        return alpha_beta_pruning_algorithm(currentDepth, currentstate, True,
                                            currentDepth + targetDepthToAdd * 2,
                                            -np.inf, np.inf, None)[1]


    def get_card_to_play(self, state):
        return self.alpha_beta_pruning(0, state, self.depth)
