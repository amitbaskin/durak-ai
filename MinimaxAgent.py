import numpy as np
from DurakSearchProblem import DurakSearchProblem


class MiniMaxAgent:
    def __init__(self, evaluation_function, players_list, nickname, depth=3):
        self.evaluation_function = evaluation_function
        self.depth = depth
        self.searcher = DurakSearchProblem(players_list, nickname)

    def minimax(self, depth, state, targetDepthToAdd):
        def minimax_algorithm(current_depth, current_state, is_max_turn,
                             target_depth, alpha, beta, current_action):
            if current_depth == target_depth:
                return self.evaluation_function(current_state), current_action

            if self.searcher.is_game_over(current_state):
                return self.evaluation_function(current_state), current_action

            if is_max_turn:
                possible_states = []
                max_eval = -np.inf, None
                for possible_card in \
                        self.searcher. \
                                get_possible_cards(current_state) + [None]:
                    temp_state = \
                        self.searcher.generate_successor(
                            current_state, possible_card)
                    if current_depth == 0 and current_action is None:
                        tenp_action = possible_card
                    else:
                        tenp_action = current_action
                    curr_eval = minimax_algorithm(current_depth + 1, temp_state,
                                                 False,
                                                 target_depth,
                                                 alpha, beta,
                                                 tenp_action)
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
                for possible_card in \
                        self.searcher. \
                                get_possible_cards(current_state) + [None]:
                    temp_state = \
                        self.searcher.generate_successor(
                            current_state, possible_card)
                    if current_depth == 0 and current_action is None:
                        tenp_action = possible_card
                    else:
                        tenp_action = current_action
                    curr_eval = minimax_algorithm(current_depth + 1, temp_state,
                                                 True,
                                                 target_depth,
                                                 alpha, beta,
                                                 tenp_action)
                    possible_states.append(curr_eval)
                    min_eval = min(min_eval, curr_eval, key=lambda x: x[0])
                    beta = min(beta, curr_eval[0])
                    if beta <= alpha:
                        break
                if len(possible_states) == 0:
                    return \
                        self.evaluation_function(current_state), current_action
                return min(possible_states, key=lambda x: x[0])

        return minimax_algorithm(depth, state, True,
                                depth + targetDepthToAdd * 2,
                                -np.inf, np.inf, None)[1]

    def get_action(self, state):
        return self.minimax(0, state, self.depth)
