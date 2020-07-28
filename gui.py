from tkinter import ttk
import tkinter as tk
from PIL import Image, ImageTk
from imageio import imread
import os
from game_mechanics import Pointer, Table, Pile
import random
from player import Player, HumanPlayer
import time
from durak_ai import AiPlayerDumb, SimplePlayer, HandicappedSimplePlayer


CARD_WIDTH = 69 + 4
CARD_HEIGHT = 94 + 4

def num_to_suit(num):
    if str(num) == num:
        return num
    suits_pack_ = ['diamonds', 'hearts', 'spades', 'clubs']
    return suits_pack_[num]


class CardFrame(ttk.Frame):
    def __init__(self, parent, card_image, highlighted=False):
        ttk.Frame.__init__(self, parent, width=CARD_WIDTH, height=CARD_HEIGHT)
        self.canvas = tk.Canvas(self, width=CARD_WIDTH, height=CARD_HEIGHT)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

        if highlighted:
            self.canvas.config(background="blue")

        self.original_img = card_image
        self.PIL_image = Image.fromarray(self.original_img)
        self.img = ImageTk.PhotoImage(image=self.PIL_image)
        self.canvas.create_image(4, 4, anchor=tk.NW, image=self.img)


class BlankCardFrame(CardFrame):
    def __init__(self, parent):
        self.original_img = imread(os.path.join("cards", "blank.png"))
        CardFrame.__init__(self, parent, self.original_img, False)


class PlayingCardFrame(CardFrame):
    def __init__(self, parent, card, highlighted=False):
        self.original_img = imread(os.path.join("cards", str(card.number) + "-" + num_to_suit(card.suit) + ".png"))
        self.card = card
        CardFrame.__init__(self, parent, self.original_img, highlighted)


class InteractablePlayingCard(PlayingCardFrame):
    def __init__(self, parent, card, num_in_hand, highlighted=False,  click_callback=None):
        PlayingCardFrame.__init__(self, parent, card, highlighted)
        self.click_callback = click_callback
        self.canvas.bind('<Button-1>', self.click)
        self.num_in_hand = num_in_hand
        self.card = card
        self.highlighted = highlighted

    def click(self, *args):
        if not self.highlighted:
            return
        self.click_callback(self.num_in_hand, self.card)


class DeckFrame(ttk.Frame):
    def __init__(self, parent, num_cards):
        ttk.Frame.__init__(self, parent, width=CARD_WIDTH + 25, height=CARD_HEIGHT + 25)
        if num_cards == 0:
            return
        self.cards = [BlankCardFrame(self) for _ in range(min(5, num_cards))]

        for i, card in enumerate(self.cards):
            card.place(x=i * min(5, num_cards), y=i * min(5, num_cards), anchor="nw")


class CardPair(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent, width=CARD_WIDTH + 25, height=CARD_HEIGHT + 25)
        self.bottom_card = None
        self.top_card = None

    def set_bottom_card(self, bottom_card):
        self.bottom_card = bottom_card
        self.update_view()

    def set_top_card(self, top_card):
        self.top_card = top_card
        self.update_view()

    def update_view(self):
        if self.bottom_card is not None:
            self.bottom_card.place(x=0, y=0, anchor="nw")
        if self.top_card is not None:
            self.top_card.place(x=15, y=15, anchor="nw")


class TableFrame(ttk.Frame):
    def __init__(self, parent):
        self.padding = 6
        width = (CARD_WIDTH + 25) * 6 + self.padding * 6
        height = (CARD_HEIGHT + 25) + self.padding
        ttk.Frame.__init__(self, parent, width=width, height=height)
        self.card_pairs = []

    def add_card_pair(self, card_pair):
        self.card_pairs.append(card_pair)

    def update_view(self):
        assert len(self.card_pairs) <= 6
        for i, card_pair in enumerate(self.card_pairs):
            card_pair.place(x=self.padding * i + (CARD_WIDTH + 15) * i, y=0, anchor="nw")

    def reset_table(self):
        for pair in self.card_pairs:
            pair.destroy()
        self.card_pairs = []


class PlayerHand(ttk.Frame):
    def __init__(self, parent, hand, options, callback, shown=True):
        self.padding = 6
        width = (CARD_WIDTH + self.padding) * len(hand)
        height = CARD_HEIGHT + self.padding * 2
        ttk.Frame.__init__(self, parent, width=width, height=height)
        self.hand = hand
        self.shown = shown
        self.callback = callback

        self.update_hand(hand, options)

    def update_hand(self, hand, options):
        for i, card in enumerate(hand):
            playing_card = InteractablePlayingCard(self, card, i, card in options,self.callback) \
                if self.shown else BlankCardFrame(self)
            playing_card.place(x=(CARD_WIDTH + self.padding) * i, y=0, anchor="nw")


class Card:
    def __init__(self, number, suit):
        self.number = number
        self.suit = suit

    def __repr__(self):
        return str(self.number) + " of " + self.suit


class Deck:
    def __init__(self):
        self.cards = []
        for i in range(6, 15):
            for suit in ["spades", "hearts", "diamonds", "clubs"]:
                self.cards.append(Card(i, suit))
        random.shuffle(self.cards)
        self.cards.insert(0, self.cards[-1])

    def draw_card(self):
        return self.cards.pop()

    def draw_cards(self, number):
        cards = []
        for _ in range(number):
            cards.append(self.draw_card())
        return cards


class Round:
    def __init__(self, players_list, deck, pile, gui):
        self.players_list = players_list
        self.deck = deck
        self.table = Table()
        self.pile = pile
        self.gui = gui

        self.draw_card_for_trump()

        self.pointer = Pointer(self.players_list, self.trump_card.suit)
        self.attacker = players_list[self.pointer.attacker_id]
        self.attacker.attacking = True
        self.defender = players_list[self.pointer.defender_id]
        self.defender.attacking = False
        self.status = None

        self.draw_cards_for_players()

    def round(self):
        pass

    def draw_card_for_trump(self):
        self.trump_card = self.deck.draw_card()

    def draw_cards_for_players(self):
        self.attacker.draw_cards(self.deck)
        self.defender.draw_cards(self.deck)

    def check_winner(self):
        winners = []
        if not self.attacker.cards:
            winners.append(self.attacker.nickname)
        if not self.defender.cards:
            winners.append(self.defender.nickname)
        if winners:
            if len(winners) == 2:
                self.status = 'Draw'
                return 'DRAW'
            else:
                self.status = winners[0]
                return 'WIN'

    def check_win(self):
        if self.deck.cards:
            pass
        else:
            return self.check_winner()


class RoundWithHuman(Round):
    def __init__(self, players_list, deck, pile, gui):
        Round.__init__(self, players_list, deck, pile, gui)
        
        self.human_player = self.attacker if self.attacker.human else self.defender
        self.attacking = self.attacker.human
        self.count = 0
        self.round_over = False

        self.status = "Attacking" if self.attacking else "Defending"

        self.round()

    def round(self):
        if self.check_win():
            print(self.status)
            self.gui.winner_decided(self.status)
            return self.status
        if not self.attacker.human:
            self.attacker.attack(self)
        self.gui.build_gui(self, self.card_pick_callback, self.status, is_attacker_first_round=self.attacking)

    def _first_stage(self, choice, card):
        if self.attacking:
            self.table.update_table(card)
            self.attacker.remove_card(card)
            if self.defender.defend(self) is None:
                self.defender.grab_table(self.table)
            self.draw_cards_for_players()
        else:
            if choice is None:
                self.attacker.draw_cards(self.deck)
                self.defender.grab_table(self.table)
                self.round_over = True
            else:
                self.table.update_table(card)
                self.defender.remove_card(card)
            self.attacker.attack(self)
            self.draw_cards_for_players()
        self.count += 1

    def swap_players(self):
        self.attacker, self.defender = self.defender, self.attacker
        self.defender.attacking = False
        self.attacker.attacking = True
        self.attacking = not self.attacking
        self.status = "Attacking" if self.attacking else "Defending"

    def second_stage_reset_round(self):
        self.round_over = True
        print('_second_stage no options for attacker')
        self.draw_cards_for_players()
        self.pile.update(self.table)
        self.table.clear()

        self.swap_players()

    def second_stage_attacking(self, choice, card):
        if choice is None:
            self.second_stage_reset_round()
            self.attacker.attack(self)
        else:
            self.table.update_table(card)
            self.attacker.remove_card(card)
            self.count += 1
            if self.defender.defend(self) is None:
                self.attacker.draw_cards(self.deck)
                self.round_over = True

    def second_stage_defending(self, choice, card):
        if choice is None:
            self.defender.grab_table(self.table)

            self.draw_cards_for_players()
            self.gui.update_gui(self, self.card_pick_callback, self.status)
            if not self.check_win():
                self.count = 0
                self.attacker.attack(self)
                self.draw_cards_for_players()
            self.gui.update_gui(self, self.card_pick_callback, self.status)
            return
        else:
            self.defender.remove_card(card)
            self.table.update_table(card)

        if self.attacker.adding_card(self) is not None:
            self.count += 1

            self.gui.update_gui(self, self.card_pick_callback, self.status)
            if self.check_win():
                self.gui.winner_decided(self.status)
            return
        else:
            self.second_stage_reset_round()

            self.gui.update_gui(self, self.card_pick_callback, self.status, is_attacker_first_round=True)
            if self.check_win():
                self.gui.winner_decided(self.status)
                return
            return False

    def second_stage_round_over(self, choice):
        if choice is None:
            self.defender.grab_table(self.table)
        else:
            self.pile.update(self.table)

        self.draw_cards_for_players()
        self.table.clear()

        self.swap_players()

        self.count = 0

    def card_pick_callback(self, choice, card):
        if self.check_win():
            self.gui.winner_decided(self.status)
            return

        if self.round_over:
            self.count = 0
            self.round_over = False

        if self.count == 0:
            self._first_stage(choice, card)
        elif 1 <= self.count < 6:  # Second stage.
            if self.attacking:
                self.second_stage_attacking(choice, card)
            else:
                return self.second_stage_defending(choice, card)
        else:
            self.second_stage_round_over(choice)

        if self.check_win():
            self.gui.winner_decided(self.status)
            return
        self.gui.update_gui(self, self.card_pick_callback, self.status)


class RoundWithAI(Round):
    def __init__(self, players_list, deck, pile, gui):
        Round.__init__(self, players_list, deck, pile, gui)

        self.status = ""
        self.player_won = False

        self.round()

    def round(self):
        self.gui.build_gui(self, None, self.status, True)
        if self.check_win():
            print(self.status)
            self.gui.winner_decided(self.status)
            return self.status
        if self._first_stage() == True:
            self.gui.update_gui(self, None, self.status, True)
            self.round()
            return "first_stage_finish"
        self.gui.update_gui(self, None, self.status, True)
        self._second_stage()

        self.round()

    def _first_stage(self):
        print(self.trump_card)
        print(self.attacker.nickname, 'num cards', len(self.attacker.cards))
        print(self.defender.nickname, 'defender num cards', len(self.defender.cards))
        print('deck num cards', len(self.deck.cards))
        if self.attacker.attack(self) == None:
            self.pile.update(self.table)
            self.table.clear()

            self.draw_cards_for_players()
            self.attacker, self.defender = self.defender, self.attacker
            self.attacker.attacking = True
            self.defender.attacking = False
            self._first_stage()
            return
        # defender can't defend
        if self.defender.defend(self) is None:
            print('_first_stage no options for defender')
            self.attacker.draw_cards(self.deck)
            return True
        # defender defended successfully
        return False

    def _second_stage(self):
        cnt = 1
        while True and cnt < 6:
            self.gui.update_gui(self, None, self.status, True)
            if self.attacker.adding_card(self) is not None:
                cnt += 1
                if self.defender.defend(self) is None:
                    print('_second_stage no options for defender')
                    self.attacker.draw_cards(self.deck)
                    return False
            else:
                print('_second_stage no options for attacker')
                self.attacker.draw_cards(self.deck)
                self.defender.draw_cards(self.deck)
                self.pile.update(self.table)
                self.table.clear()
                self.attacker, self.defender = self.defender, self.attacker
                self.attacker.attacking = True
                self.defender.attacking = False
                self.gui.update_gui(self, None, self.status, True)
                return False
        print('second_stage no cards')


class DurakGame:
    def __init__(self, gui, player_list):
        self.deck = Deck()
        self.player_list = player_list
        self.pile = Pile()
        self.gui = gui
        self.is_human_playing = False
        for player in player_list:
            if player.human:
                self.is_human_playing = True

        self.curr_round = None
        self.round()

    def round(self):
        if self.is_human_playing:
            self.curr_round = RoundWithHuman(self.player_list, self.deck, self.pile, self.gui)
        else:
            self.curr_round = RoundWithAI(self.player_list, self.deck, self.pile, self.gui)


class Durak_GUI(tk.Tk):
    def __init__(self, players_list, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "Durak")

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.player_list = players_list

        self.winners = []
        self.amount_of_games = 0
        self.amount_of_games_won = 0

        self.after(0, func=self.start_game)

    def start_game(self):
        for player in self.player_list:
            player._refresh()
        self.game = DurakGame(self, self.player_list)

    def winner_decided(self, nickname):
        self.winners.append(nickname)

        self.amount_of_games += 1
        self.amount_of_games_won += 1 if nickname == self.player_list[1].nickname else 0

        self.container.destroy()
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)

        self.winner_label = ttk.Label(self.container, text=nickname + " has won!!!!", font=('Helvetica', 25))
        self.winner_label.pack()

        if self.amount_of_games < 50:
            self.after(0, func=self.start_game)
        else:
            print("Player 2 win rate:", self.amount_of_games_won / self.amount_of_games)

        # self.replay_button = ttk.Button(self.container, text="New Game", command=self.start_game)
        # self.replay_button.pack()

    def update_gui(self, game, choose_card_callback, status, show_all=False, is_attacker_first_round=False):
        self.enemy_player_hand.destroy()
        self.enemy_player_hand = PlayerHand(self.container, self.player_list[0].cards, [], choose_card_callback,
                                            shown=show_all)
        self.enemy_player_hand.grid(row=0, column=1)

        self.attacking_label.configure(text=status)

        self.table.reset_table()
        for i in range(0, len(game.table.cards), 2):
            pair = CardPair(self.table)
            bottom_card = PlayingCardFrame(pair, game.table.cards[i])
            pair.set_bottom_card(bottom_card)
            if i + 1 < len(game.table.cards):
                top_card = PlayingCardFrame(pair, game.table.cards[i+1])
                pair.set_top_card(top_card)
            self.table.add_card_pair(pair)
        self.table.update_view()

        self.deck.destroy()
        self.deck = DeckFrame(self.container, len(game.deck.cards))
        self.deck.grid(row=1, column=2)

        playable_cards = self.player_list[1].options(game.table, game.trump_card.suit)
        self.player_hand.destroy()
        self.player_hand = PlayerHand(self.container, self.player_list[1].cards,
                                      playable_cards, choose_card_callback, shown=True)
        self.player_hand.grid(row=2, column=1)

        if not is_attacker_first_round:
            self.admit_defeat.grid(row=2, column=2)
        else:
            self.admit_defeat.grid_forget()
        tk.Tk.update(self)

    def build_gui(self, game, choose_card_callback, status, show_all=False, is_attacker_first_round=False):
        if self.container is not None:
            self.container.destroy()
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)

        self.enemy_label = ttk.Label(self.container, text=self.player_list[0].nickname)
        self.enemy_label.grid(row=0, column=0)

        self.enemy_player_hand = PlayerHand(self.container, self.player_list[0].cards, [], choose_card_callback, shown=show_all)
        self.enemy_player_hand.grid(row=0, column=1)

        self.attacking_label = ttk.Label(self.container, text=status)
        self.attacking_label.grid(row=1, column=0)

        self.table = TableFrame(self.container)
        self.table.grid(row=1, column=1)

        for i in range(0, len(game.table.cards), 2):
            pair = CardPair(self.table)
            bottom_card = PlayingCardFrame(pair, game.table.cards[i])
            pair.set_bottom_card(bottom_card)
            if i + 1 < len(game.table.cards):
                top_card = PlayingCardFrame(pair, game.table.cards[i+1])
                pair.set_top_card(top_card)
            self.table.add_card_pair(pair)
        self.table.update_view()

        self.deck = DeckFrame(self.container, len(game.deck.cards))
        self.deck.grid(row=1, column=2)

        self.trump_card = PlayingCardFrame(self.container, game.trump_card)
        self.trump_card.grid(row=1, column=3)

        self.player_label = ttk.Label(self.container, text=self.player_list[1].nickname)
        self.player_label.grid(row=2, column=0)

        playable_cards = self.player_list[1].options(game.table, game.trump_card.suit)
        self.player_hand = PlayerHand(self.container, self.player_list[1].cards,
                                      playable_cards, choose_card_callback, shown=True)
        self.player_hand.grid(row=2, column=1)

        self.admit_defeat = ttk.Button(self.container, text="Forfeit round",
                                       command=lambda: choose_card_callback(None, None))
        self.admit_defeat.grid(row=2, column=2)
        if is_attacker_first_round:
            self.admit_defeat.grid_forget()
        tk.Tk.update(self)


if __name__ == "__main__":
    player1 = HandicappedSimplePlayer("Wall E")
    player2 = SimplePlayer("Eva")
    # player2 = HumanPlayer("Eva")
    app = Durak_GUI([player1, player2], None)
    app.mainloop()
