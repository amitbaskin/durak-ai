import abc
import numpy as np
from DurakSearchProblem import DurakSearchProblem


class Agent:

    @abc.abstractmethod
    def get_card_to_play(self, state):
        return


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

    def minmax(self, current_depth, current_state,
               target_depth_to_add):
        def minmax_algorithm(depth, state, max_turn,
                             target_depth, alpha, beta,
                             card_to_play):
            if depth == target_depth:
                return self.evaluation_function(state), card_to_play

            if self.searcher.is_game_over(state):
                return self.evaluation_function(state), card_to_play

            if max_turn:
                possible_states = []
                max_eval = -np.inf, None
                for possible_card in self.searcher.get_possible_cards(
                        state) + [None]:
                    state = self.searcher.generate_successor(state,
                                                             possible_card)
                    if depth == 0 and card_to_play is None:
                        curr_action = possible_card
                    else:
                        curr_action = card_to_play
                    curr_eval = minmax_algorithm(depth + 1, state,
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
                    return self.evaluation_function(state), card_to_play
                return max(possible_states, key=lambda x: x[0])

            else:
                possible_states = []
                min_eval = np.inf, None
                for possible_card in self.searcher.get_possible_cards(
                        state) + [None]:
                    state = self.searcher.generate_successor(state,
                                                             possible_card)
                    if depth == 0 and card_to_play is None:
                        curr_action = possible_card
                    else:
                        curr_action = card_to_play
                    curr_eval = minmax_algorithm(depth + 1, state,
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
                    return self.evaluation_function(state), card_to_play
                return min(possible_states, key=lambda x: x[0])

        return minmax_algorithm(current_depth, current_state, True,
                                current_depth + target_depth_to_add * 2,
                                -np.inf, np.inf, None)[1]

    def get_card_to_play(self, state):
        return self.minmax(0, state, self.depth)
