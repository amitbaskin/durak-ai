def minmax(self, current_depth, current_state, target_depth_to_add):
    def minmax_algorithm(depth, state, max_turn,
                         target_depth, card_to_play):
        if depth == target_depth:
            return self.evaluation_function(state), card_to_play

        if self.searcher.is_game_over(state):
            return self.evaluation_function(state), card_to_play

        if max_turn:
            possible_states = []
            options = self.searcher.get_possible_cards(state)
            for possible_card in options:
                state = self.searcher.generate_successor(
                    state, possible_card)
                if depth == 0 and card_to_play is None:
                    current_card_to_play = possible_card
                else:
                    current_card_to_play = card_to_play

                possible_states.append(
                    minmax_algorithm(depth + 1, state, False,
                                     target_depth,
                                     current_card_to_play))
            if len(possible_states) == 0:
                return -np.inf, card_to_play
            return max(possible_states, key=lambda x: x[0])

        else:
            possible_states = []
            for possible_card in self.searcher.get_possible_cards(state):
                state = self.searcher.generate_successor(state,
                                                         possible_card)
                if depth == 0 and card_to_play is None:
                    current_action = possible_card
                else:
                    current_action = card_to_play
                possible_states.append(
                    minmax_algorithm(depth + 1, state, True,
                                     target_depth,
                                     current_action))
            if len(possible_states) == 0:
                return self.evaluation_function(state), card_to_play
            return min(possible_states, key=lambda x: x[0])

    return minmax_algorithm(
        current_depth, current_state, True,
        current_depth + target_depth_to_add * 2, None)[1]