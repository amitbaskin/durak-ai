import numpy as np
from DurakSearchProblem import DurakSearchProblem


def print_state(state, possible_action):
    print("trump card: ", state.trump_card)
    print("possible_action: ", possible_action)
    print("current_player:", state.current_player.nickname)
    print("is current_player attacking:",
          state.current_player.attacking)
    print("attacker:", state.attacker.nickname)
    print("is attacker attacking:",
          state.attacker.attacking)
    print("attacker cards: ", state.attacker.get_cards())
    print("defender:", state.defender.nickname)
    print("is defender attacking:",
          state.defender.attacking)
    print("defender cards: ", state.defender.get_cards())
    print("table: ", state.table.get_cards())


class MiniMaxAgent:
    def __init__(self, evaluation_function, players_list, nickname, depth=5):
        self.evaluation_function = evaluation_function
        self.depth = depth
        self.searcher = DurakSearchProblem(players_list, nickname)

    def minmax(self, current_depth, current_state,
               target_depth_to_add):
        def minmax_algorithm(depth, state, max_turn,
                             target_depth, alpha, beta,
                             action):
            if depth == target_depth:
                return self.evaluation_function(state), action

            if self.searcher.is_game_over(state):
                return self.evaluation_function(state), action

            if max_turn:
                possible_states = []
                max_eval = -np.inf, None
                options = self.searcher.get_possible_cards(state) + [None]
                for possible_action in options:
                    print_state(state, possible_action)
                    state = self.searcher.generate_successor(state,
                                                             possible_action)
                    print_state(state, possible_action)
                    if depth == 0 and action is None:
                        current_action = possible_action
                    else:
                        current_action = action
                    curr_eval = minmax_algorithm(depth + 1, state,
                                                 False,
                                                 target_depth,
                                                 alpha, beta,
                                                 current_action)
                    possible_states.append(curr_eval)
                    max_eval = max(max_eval, curr_eval, key=lambda x: x[0])
                    alpha = max(alpha, curr_eval[0])
                    if beta <= alpha:
                        break
                if len(possible_states) == 0:
                    return self.evaluation_function(state), action
                return max(possible_states, key=lambda x: x[0])

            else:
                possible_states = []
                min_eval = np.inf, None
                options = self.searcher.get_possible_cards(state) + [None]
                for possible_action in options:
                    print_state(state, possible_action)
                    state = self.searcher.generate_successor(state,
                                                             possible_action)
                    print_state(state, possible_action)
                    if depth == 0 and action is None:
                        current_action = possible_action
                    else:
                        current_action = action
                    curr_eval = minmax_algorithm(depth + 1, state,
                                                 True,
                                                 target_depth,
                                                 alpha, beta,
                                                 current_action)
                    possible_states.append(curr_eval)
                    min_eval = min(min_eval, curr_eval, key=lambda x: x[0])
                    beta = min(beta, curr_eval[0])
                    if beta <= alpha:
                        break
                if len(possible_states) == 0:
                    return self.evaluation_function(state), action
                return min(possible_states, key=lambda x: x[0])

        return minmax_algorithm(current_depth, current_state, True,
                                current_depth + target_depth_to_add * 2,
                                -np.inf, np.inf, None)[1]

    def get_card_to_play(self, state):
        return self.minmax(0, state, self.depth)
