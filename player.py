from game_mechanics import CardsHolder


NO_CARDS_MSG = 'has no cards to add'
FEATURING_TABLE_MSG = 'table: '
ADDING_CARD_MSG = 'adds'
NO_DEFENCE_MSG = "can't defend"
DEFENCE_MSG = 'defends with'
ATTACK_MSG = 'attacks with'


def choose_min_card(possible_cards, trump_suit):
    trump_cards = [card for card in possible_cards if card.suit == trump_suit]
    non_trump_cards = [card for card in possible_cards if card.suit != trump_suit]

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
        self.minMaxAgent = None
        self.qAgent = None

    def play_move(self, round):
        if self.attacking:
            if len(round.table.playerCards) == 0:
                return self.attack(round)
            else:
                return self.adding_card(round)
        else:
            return self.defend(round)

    def attack_helper(self, attack_card, round):
        prev_round = round.copy()
        self.remove_card(attack_card)
        round.table.add_single_card(attack_card)
        print('{} {} {}'.format(self.nickname, ATTACK_MSG,
                                attack_card.__repr__()))
        print('{} {}'.format(FEATURING_TABLE_MSG, round.table.get_cards()))
        if self.qAgent is not None:
            # TODO:: Make round evaluation better?
            delta_reward = self.round_evaluation(round) - self.round_evaluation(prev_round)
            self.qAgent.observeTransition(prev_round, attack_card, round, delta_reward)
        return attack_card

    def add_card_helper(self, card_to_add, round):
        prev_round = round.copy()
        self.remove_card(card_to_add)
        round.table.add_single_card(card_to_add)
        print('{} {} {}'.format(self.nickname, ADDING_CARD_MSG, card_to_add))
        print(FEATURING_TABLE_MSG, round.table.get_cards())
        if self.qAgent is not None:
            # TODO:: Make round evaluation better?
            delta_reward = self.round_evaluation(round) - self.round_evaluation(prev_round)
            self.qAgent.observeTransition(prev_round, card_to_add, round, delta_reward)
        return card_to_add

    def no_cards_msg(self, round):
        print('{} {}'.format(self.nickname, NO_CARDS_MSG))
        print('{} {}'.format(FEATURING_TABLE_MSG, round.table.get_cards()))

    def defence_helper(self, defence_card, round):
        prev_round = round.copy()
        self.remove_card(defence_card)
        round.table.add_single_card(defence_card)
        print('{} {} {}'.format(self.nickname, DEFENCE_MSG, defence_card))
        print(FEATURING_TABLE_MSG, round.table.get_cards())
        if self.qAgent is not None:
            # TODO:: Make round evaluation better?
            delta_reward = self.round_evaluation(round) - self.round_evaluation(prev_round)
            self.qAgent.observeTransition(prev_round, defence_card, round, delta_reward)
        return defence_card

    def no_defence(self, round):
        print(r"{} {}".format(self.nickname, NO_DEFENCE_MSG))
        print(FEATURING_TABLE_MSG, round.table.get_cards())
        self.grab_table(round.table)

    def add_card_minimax(self, possible_cards, round):
        card_to_add = self.minMaxAgent.get_card_to_play(round)
        if card_to_add is None:
            card_to_add = choose_min_card(possible_cards,
                                          round.trump_card.suit)
            return self.add_card_helper(card_to_add, round)

    def add_card_q_learning(self, possible_cards, round):
        if possible_cards:
            card_to_add = self.qAgent.getAction(round)
            if card_to_add is None:
                card_to_add = choose_min_card(possible_cards,
                                              round.trump_card.suit)
            return self.add_card_helper(card_to_add, round)

    def q_learning_defence(self, possible_cards, round):
        if possible_cards:
            defence_card = self.qAgent.getAction(round)
            if defence_card is None:
                defence_card = choose_min_card(possible_cards,
                                              round.trump_card.suit)
            return self.defence_helper(defence_card, round)
        self.no_defence(round)

    def minMax_defence(self, possible_cards, round):
        if possible_cards:
            defence_card = self.minMaxAgent.get_card_to_play(round)
            if defence_card is None:
                defence_card = choose_min_card(possible_cards,
                                               round.trump_card.suit)
            if defence_card is not None:
                self.remove_card(defence_card)
                round.table.add_single_card(defence_card)
                print('{} {} {}'.format(self.nickname, DEFENCE_MSG,
                                        defence_card))
                print(FEATURING_TABLE_MSG, round.table.get_cards())
                return defence_card
        print(r"{} {}".format(self.nickname, NO_DEFENCE_MSG))
        print(FEATURING_TABLE_MSG, round.table.get_cards())
        self.grab_table(round.table)

    def attack(self, round):
        return None

    def defend(self, round):
        return None

    def adding_card(self, round):
        return None

    def options(self, table, trump_suit):
        if self.attacking:
            return self.attacking_options(table)
        return self.defending_options(table, trump_suit)

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


    def attacking_options(self, table):
        if len(table.get_cards()) == 0:
            return self.get_cards()

        return self.adding_card_options(table)

    def adding_card_options(self, table):
        table_card_types = [i.number for i in table.get_cards()]
        potential_cards = [card for card in self.get_cards() if card.number in
                           table_card_types]
        return potential_cards

    def defending_options(self, table, trump_suit):
        # For the gui
        if len(table.get_cards()) == 0:
            return []

        attacking_card = table.get_cards()[-1]

        # Checking if attacking_card (last card on a table) is trump.
        if attacking_card.suit == trump_suit:
            return [card for card in self.get_cards() if (card.suit == trump_suit and
                                                card.number >= attacking_card.number)]

        # Checking possible options to beat non trump card.
        non_trump_options = [card for card in self.get_cards() if
                             (card.suit == attacking_card.suit and card.number >= attacking_card.number)]
        trump_cards = [card for card in self.get_cards() if card.suit == trump_suit]
        return non_trump_options + trump_cards

    def grab_table(self, table):
        self.add_cards(table.get_cards())
        table.clear_cards()

    def _refresh(self):
        self.clear_cards()


class HumanPlayer(Player):
    def __init__(self, nickname):
        super().__init__(nickname, [])
        self.human = True

    def attack(self, round):
        #print('n', print(len(self.cards)))
        #print(table.cards)
        print("Your Turn to attack, {}:".format(self.nickname))
        attack_card_num = input('{}\nPick a card number from 0 till {} '
                                .format(self.attacking_options(), len(self.attacking_options())-1))
        attack_card = self.attacking_options()[int(attack_card_num)]
        print('card {} added'.format(attack_card))
        self.remove_card(attack_card)
        round.table.add_single_card(attack_card)
        return attack_card

    def defend(self, round):
        print('T: {}'.format(round.table.get_cards_strs()))
        #print('n', print(len(self.cards)))
        #print(table.cards)
        print(self.cards)
        if self.defending_options(round.table, round.trump_card):
            print("Your Turn to defend, {}:".format(self.nickname))
            def_card_num = input("{}\nPick a card number from 0 till {}\n'g' to grab cards\n't' to check table\n"
                                 .format(self.defending_options(round.table, round.trump_card),
                                         len(self.defending_options(round.table, round.trump_card))-1))
            if def_card_num == 'g':
                self.grab_table(round.table)
                return None
            elif def_card_num == 't':
                return 'T: {}'.format(self.defend(round))
            #elif def_card_num == 'c':
            #    return self.cards
            defend_card = self.defending_options(round.table, round.trump_card)[int(def_card_num)]
            print('card {} added'.format(defend_card))
            self.remove_card(defend_card)
            round.table.add_single_card(defend_card)
            return defend_card
        print(r"you can't defend, {}".format(self.nickname))
        self.grab_table(round.table)
        return None

    def adding_card(self, round):
        #print('n', print(len(self.cards)))
        if self.adding_card_options(round.table):
            #print('T: {}'.format(table.show()))
            print("Add card, {}:".format(self.nickname))
            adding_card_num = input("{}\nPick a card number from 0 till {}\n'p' to pass\n"
                                    .format(self.adding_card_options(round.table),
                                            len(self.adding_card_options(round.table))-1))
            if adding_card_num == 'p':
                return None
            card_to_add = self.adding_card_options(round.table)[int(adding_card_num)]
            print('card {} added'.format(card_to_add))
            self.remove_card(card_to_add)
            round.table.add_single_card(card_to_add)
            print('T: {}'.format(round.table.get_cards_strs()))
            return card_to_add
        return None
