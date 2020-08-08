from game_mechanics import CardsHolder
import abc


NO_CARDS_MSG = 'has no cards to add'
FEATURING_TABLE_MSG = 'table: '
ADDING_CARD_MSG = 'adds'
NO_DEFENCE_MSG = "can't defend"
DEFENCE_MSG = 'defends with'
ATTACK_MSG = 'attacks with'


def choose_min_card(possible_cards, trump_suit):
    trump_cards = [card for card in possible_cards if card.suit == trump_suit]
    non_trump_cards = [
        card for card in possible_cards if card.suit != trump_suit]
    non_trump_cards.sort(key=lambda x: x.number)
    if len(non_trump_cards) == 0:
        trump_cards.sort(key=lambda x: x.number)
        return trump_cards[0]
    return non_trump_cards[0]


class Player(CardsHolder):
    def __init__(self, nickname, cards):
        super().__init__(cards)
        self.nickname = nickname
        self.human = False
        self.attacking = False
        self.minmax_agent = None
        self.q_agent = None

    @abc.abstractmethod
    def attack(self, state):
        return None

    @abc.abstractmethod
    def defend(self, state):
        return None

    @abc.abstractmethod
    def add_card(self, state):
        return None

    def get_opponent(self, state):
        if self.nickname == state.attacker.nickname:
            return state.defender
        return state.attacker

    def generic_state_evaluation(self, state, get_opponnent_ptr):
        me = state.attacker if self.attacking else state.defender
        my_cards_amount = len(me.get_cards())
        opponent_cards = get_opponnent_ptr(state).get_cards()
        opponent_cards_amount = len(opponent_cards)
        if my_cards_amount == 0 and \
                opponent_cards_amount > 0 and len(state.deck.get_cards()) == 0:
            ret = 100  # Big enough than 36 possible diff
        else:
            ret = len(opponent_cards) - len(self.get_cards())
        return ret

    # TODO:: Make state evaluation better?
    def state_evaluation_delta(
            self, first_state, second_state, get_opponnent_ptr):
        first_score = \
            self.generic_state_evaluation(first_state, get_opponnent_ptr)
        second_score = \
            self.generic_state_evaluation(second_state, get_opponnent_ptr)
        if first_score == 100 and first_score == second_score:
            return first_score

        return second_score - first_score
    
    # TODO: Delete this?
    def play_move(self, state):
        if self.attacking:
            if len(state.table.playerCards) == 0:
                return self.attack(state)
            else:
                return self.add_card(state)
        else:
            return self.defend(state)

    def attack_helper(self, attack_card, state):
        prev_state = state.copy()
        self.remove_card(attack_card)
        state.table.add_single_card(attack_card)
        print('{} {} {}'.format(self.nickname, ATTACK_MSG,
                                attack_card.__repr__()))
        print('{} {}'.format(FEATURING_TABLE_MSG, state.table.get_cards()))
        if self.q_agent is not None:
            delta_reward = self.state_evaluation_delta(
                prev_state, state, self.get_opponent)
            self.q_agent.observeTransition(
                prev_state, attack_card, state, delta_reward)
        return attack_card

    def add_card_helper(self, card_to_add, state):
        prev_state = state.copy()
        self.remove_card(card_to_add)
        state.table.add_single_card(card_to_add)
        print('{} {} {}'.format(self.nickname, ADDING_CARD_MSG, card_to_add))
        print(FEATURING_TABLE_MSG, state.table.get_cards())
        if self.q_agent is not None:
            # TODO:: Make state evaluation better?
            delta_reward = self.state_evaluation_delta(
                prev_state, state, self.get_opponent)
            self.q_agent.observeTransition(
                prev_state, card_to_add, state, delta_reward)
        return card_to_add

    def no_cards_msg(self, state):
        print('{} {}'.format(self.nickname, NO_CARDS_MSG))
        print('{} {}'.format(FEATURING_TABLE_MSG, state.table.get_cards()))

    def defence_helper(self, defence_card, state):
        prev_state = state.copy()
        self.remove_card(defence_card)
        state.table.add_single_card(defence_card)
        print('{} {} {}'.format(self.nickname, DEFENCE_MSG, defence_card))
        print(FEATURING_TABLE_MSG, state.table.get_cards())
        if self.q_agent is not None:
            # TODO:: Make state evaluation better?
            delta_reward = self.state_evaluation_delta(
                prev_state, state, self.get_opponent)
            self.q_agent.observeTransition(
                prev_state, defence_card, state, delta_reward)
        return defence_card

    def no_defence(self, state):
        print(r"{} {}".format(self.nickname, NO_DEFENCE_MSG))
        print(FEATURING_TABLE_MSG, state.table.get_cards())
        self.grab_table(state.table)

    def add_card_minimax(self, possible_cards, state):
        card_to_add = self.minmax_agent.get_card_to_play(state)
        if card_to_add is None:
            card_to_add = choose_min_card(possible_cards,
                                          state.trump_card.suit)
            return self.add_card_helper(card_to_add, state)

    def add_card_q_learning(self, possible_cards, state):
        if possible_cards:
            card_to_add = self.q_agent.getAction(state)
            if card_to_add is None:
                card_to_add = choose_min_card(possible_cards,
                                              state.trump_card.suit)
            return self.add_card_helper(card_to_add, state)

    def q_learning_defence(self, possible_cards, state):
        if possible_cards:
            defence_card = self.q_agent.getAction(state)
            if defence_card is None:
                defence_card = choose_min_card(possible_cards,
                                              state.trump_card.suit)
            return self.defence_helper(defence_card, state)
        self.no_defence(state)

    def minmax_defence(self, possible_cards, state):
        if possible_cards:
            defence_card = self.minmax_agent.get_card_to_play(state)
            if defence_card is None:
                defence_card = choose_min_card(possible_cards,
                                               state.trump_card.suit)
            if defence_card is not None:
                self.remove_card(defence_card)
                state.table.add_single_card(defence_card)
                print('{} {} {}'.format(self.nickname, DEFENCE_MSG,
                                        defence_card))
                print(FEATURING_TABLE_MSG, state.table.get_cards())
                return defence_card
        print(r"{} {}".format(self.nickname, NO_DEFENCE_MSG))
        print(FEATURING_TABLE_MSG, state.table.get_cards())
        self.grab_table(state.table)

    def options(self, table, trump_suit):
        if self.attacking:
            return self.get_attack_options(table)
        return self.get_defence_options(table, trump_suit)

    def draw_cards(self, deck_instance):
        n_cards_to_draw = 6 - len(self.get_cards())
        if n_cards_to_draw < 0:
            n_cards_to_draw = 0
        n_of_cards_left = len(deck_instance.get_cards())
        if n_of_cards_left > n_cards_to_draw:
            self.add_cards(deck_instance.draw_cards(n_cards_to_draw))
        elif n_of_cards_left <= n_cards_to_draw:
            self.add_cards(deck_instance.draw_cards(n_of_cards_left))
        else:
            print('no cards to draw')

    def get_attack_options(self, table):
        if len(table.get_cards()) == 0:
            return self.get_cards()
        return self.adding_card_options(table)
    
    def get_defence_options(self, table, trump_suit):
        # For the gui
        if len(table.get_cards()) == 0:
            return []
        attack_card = table.get_cards()[-1]
        # Checking if attacking_card (last card on a table) is trump
        if attack_card.suit == trump_suit:
            return [card for card in self.get_cards() 
                    if (card.suit == trump_suit and 
                        card.number >= attack_card.number)]
        # Checking possible options to beat non trump card
        non_trump_options = [card for card in self.get_cards() if
                             (card.suit == attack_card.suit
                              and card.number >= attack_card.number)]
        trump_cards = [card for card in self.get_cards() if
                       card.suit == trump_suit]
        return non_trump_options + trump_cards

    def adding_card_options(self, table):
        table_card_types = [i.number for i in table.get_cards()]
        potential_cards = [card for card in self.get_cards() if card.number in
                           table_card_types]
        return potential_cards

    def grab_table(self, table):
        self.add_cards(table.get_cards())
        table.clear_cards()


class HumanPlayer(Player):
    def __init__(self, nickname):
        super().__init__(nickname, [])
        self.human = True

    def attack(self, state):
        print("Your Turn to attack, {}:".format(self.nickname))
        attack_card_num = \
            input('{}\nPick a card number from 0 till {} '.
                  format(self.get_attack_options(state.table),
                         len(self.get_attack_options(state.table)) - 1))
        attack_card = self.get_attack_options(state.table)[int(attack_card_num)]
        print('card {} added'.format(attack_card))
        self.remove_card(attack_card)
        state.table.add_single_card(attack_card)
        return attack_card

    def defend(self, state):
        print('T: {}'.format(state.table.get_cards_strs()))
        print(self.cards)
        if self.get_defence_options(state.table, state.trump_card):
            print("Your Turn to defend, {}:".format(self.nickname))
            def_card_num = input("{}\nPick a card number from 0 till "
                                 "{}\n'g' to grab cards\n't' to check table\n"
                                 .format(self.get_defence_options(
                state.table, state.trump_card),
                len(self.get_defence_options(
                                             state.table, state.trump_card)) - 1))
            if def_card_num == 'g':
                self.grab_table(state.table)
                return None
            elif def_card_num == 't':
                return 'T: {}'.format(self.defend(state))
            defend_card = self.get_defence_options(
                state.table, state.trump_card)[int(def_card_num)]
            print('card {} added'.format(defend_card))
            self.remove_card(defend_card)
            state.table.add_single_card(defend_card)
            return defend_card
        print(r"you can't defend, {}".format(self.nickname))
        self.grab_table(state.table)
        return None

    def add_card(self, state):
        if self.adding_card_options(state.table):
            print("Add card, {}:".format(self.nickname))
            adding_card_num = input(
                "{}\nPick a card number from 0 till {}\n'p' to pass\n"
                                    .format(
                    self.adding_card_options(state.table),
                    len(self.adding_card_options(
                                                state.table)) - 1))
            if adding_card_num == 'p':
                return None
            card_to_add = self.adding_card_options(
                state.table)[int(adding_card_num)]
            print('card {} added'.format(card_to_add))
            self.remove_card(card_to_add)
            state.table.add_single_card(card_to_add)
            print('T: {}'.format(state.table.get_cards_strs()))
            return card_to_add
        return None
