import numpy as np
from DurakSearchProblem import DurakSearchProblem


class MiniMaxAgent:
    def __init__(self, evaluation_function, players_list, nickname, depth=3):
        self.evaluation_function = evaluation_function
        self.depth = depth
        self.searcher = DurakSearchProblem(players_list, nickname)

    def minmax(self, state):
        def minmax_algorithm(current_depth, current_state, is_max_turn,
                             alpha, beta, current_action):

            if current_depth == self.depth:
                return self.evaluation_function(current_state), current_action

            if self.searcher.is_game_over(current_state):
                return self.evaluation_function(current_state), current_action

            if is_max_turn:
                possible_states = []
                max_eval = -np.inf, None
                for possible_action in self.searcher.get_possible_cards(
                        current_state) + [None]:
                    temp_state = self.searcher.generate_successor(
                        current_state, possible_action)
                    if current_depth == 0 and current_action is None:
                        temp_action = possible_action
                    else:
                        temp_action = current_action
                    curr_eval = minmax_algorithm(current_depth + 1, temp_state,
                                                 False,
                                                 alpha, beta,
                                                 temp_action)
                    possible_states.append(curr_eval)
                    max_eval = max(max_eval, curr_eval, key=lambda x: x[0])
                    alpha = max(alpha, curr_eval[0])
                    if beta <= alpha:
                        break
                if len(possible_states) == 0:
                    return self.evaluation_function(current_state), \
                           current_action
                return max(possible_states, key=lambda x: x[0])

            else:
                possible_states = []
                min_eval = np.inf, None
                for possible_action in self.searcher.get_possible_cards(
                        current_state) + [None]:
                    temp_state = self.searcher.generate_successor(
                        current_state, possible_action)
                    if current_depth == 0 and current_action is None:
                        temp_action = possible_action
                    else:
                        temp_action = current_action
                    curr_eval = minmax_algorithm(current_depth + 1, temp_state,
                                                 True,
                                                 alpha, beta,
                                                 temp_action)
                    possible_states.append(curr_eval)
                    min_eval = min(min_eval, curr_eval, key=lambda x: x[0])
                    beta = min(beta, curr_eval[0])
                    if beta <= alpha:
                        break
                if len(possible_states) == 0:
                    return \
                        self.evaluation_function(current_state), current_action
                return min(possible_states, key=lambda x: x[0])

        return minmax_algorithm(0, state, True, -np.inf, np.inf, None)[1]

    def get_action(self, state):
        return self.minmax(state)
