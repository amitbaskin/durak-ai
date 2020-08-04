import abc
import numpy as np
from DurakSearchProblem import DurakSearchProblem

class Agent(object):
    def __init__(self):
        super(Agent, self).__init__()

    @abc.abstractmethod
    def get_card_to_play(self, round):
        return

    def stop_running(self):
        pass


class MultiAgentSearchAgent(Agent):
    def __init__(self, evaluation_function, depth=3):
        super().__init__()
        self.evaluation_function = evaluation_function
        self.depth = depth

    @abc.abstractmethod
    def get_card_to_play(self, round):
        return


class MiniMaxAgent(MultiAgentSearchAgent):
    def __init__(self, evaluation_function, players_list, nickname):
        super().__init__(evaluation_function)
        self.searcher = DurakSearchProblem(players_list, nickname)

    def minimax(self, currentDepth, current_round,  targetDepthToAdd):
        def minimax_algorithm(depth, curr_round, max_turn,
                              target_depth, card_to_play):
            if depth == target_depth:
                return self.evaluation_function(curr_round), card_to_play

            if max_turn:
                possible_rounds = []
                for possible_card in self.searcher.get_possible_cards(curr_round):
                    round = self.searcher.generate_successor(curr_round, possible_card)
                    if card_to_play is None:
                        curr_card_to_play = possible_card
                    else:
                        curr_card_to_play = card_to_play
                    possible_rounds.append(
                        minimax_algorithm(depth + 1, round, False,
                                          target_depth,
                                          curr_card_to_play))
                if len(possible_rounds) == 0:
                    return -np.inf, card_to_play
                return max(possible_rounds, key=lambda x: x[0])

            else:
                possible_rounds = []
                for possible_card in self.searcher.get_possible_cards(curr_round):
                    round = self.searcher.generate_successor(curr_round, possible_card)
                    if card_to_play is None:
                        curr_card_to_play = possible_card
                    else:
                        curr_card_to_play = card_to_play
                    possible_rounds.append(
                        minimax_algorithm(depth + 1, round, True,
                                          target_depth,
                                          curr_card_to_play))
                if len(possible_rounds) == 0:
                    return self.evaluation_function(curr_round), card_to_play
                return min(possible_rounds, key=lambda x: x[0])

        return minimax_algorithm(currentDepth, current_round, True,
                                 currentDepth + targetDepthToAdd * 2, None)[1]

    def alpha_beta_pruning(self, currentDepth, currentRound,
                           targetDepthToAdd):
        def alpha_beta_pruning_algorithm(depth, curr_round, max_turn, target_depth, alpha, beta, card_to_play):
            if depth == target_depth:
                return self.evaluation_function(curr_round), card_to_play

            if self.searcher.is_game_over(curr_round):
                return self.evaluation_function(curr_round), card_to_play

            if max_turn:
                possible_states = []
                max_eval = -np.inf, None
                for possible_card in self.searcher.get_possible_cards(curr_round) + [None]:
                    round = self.searcher.generate_successor(curr_round, possible_card)
                    if depth == 0 and card_to_play is None:
                        curr_action = possible_card
                    else:
                        curr_action = card_to_play
                    curr_eval = alpha_beta_pruning_algorithm(depth + 1, round,
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
                    return self.evaluation_function(curr_round), card_to_play
                return max(possible_states, key=lambda x: x[0])

            else:
                possible_states = []
                min_eval = np.inf, None
                for possible_card in self.searcher.get_possible_cards(curr_round) + [None]:
                    round = self.searcher.generate_successor(curr_round, possible_card)
                    if depth == 0 and card_to_play is None:
                        curr_action = possible_card
                    else:
                        curr_action = card_to_play
                    curr_eval = alpha_beta_pruning_algorithm(depth + 1, round,
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
                    return self.evaluation_function(curr_round), card_to_play
                return min(possible_states, key=lambda x: x[0])

        return alpha_beta_pruning_algorithm(currentDepth, currentRound, True,
                                            currentDepth + targetDepthToAdd * 2,
                                            -np.inf, np.inf, None)[1]


    def get_card_to_play(self, round):
        return self.alpha_beta_pruning(0, round, self.depth)
