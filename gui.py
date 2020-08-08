import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from imageio import imread
from DurakAi import *
from Player import *
from game_mechanics import *


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
        self.original_img = \
            imread(os.path.join("cards", str(card.number) +
                                "-" + num_to_suit(card.suit) + ".png"))
        self.card = card
        CardFrame.__init__(self, parent, self.original_img, highlighted)


class InteractablePlayingCard(PlayingCardFrame):
    def __init__(self, parent, card, num_in_hand,
                 highlighted=False, click_callback=None):
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
        ttk.Frame.__init__(self, parent, width=CARD_WIDTH + 25,
                           height=CARD_HEIGHT + 25)
        if num_cards == 0:
            return
        self.cards = [BlankCardFrame(self) for _ in range(min(5, num_cards))]

        for i, card in enumerate(self.cards):
            card.place(x=i * min(5, num_cards), y=i * min(5, num_cards),
                       anchor="nw")


class CardPair(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent, width=CARD_WIDTH + 25,
                           height=CARD_HEIGHT + 25)
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
        for i, card_pair in enumerate(self.card_pairs):
            card_pair.place(x=self.padding * i + (CARD_WIDTH + 15) * i, y=0,
                            anchor="nw")

    def reset_table(self):
        for pair in self.card_pairs:
            pair.destroy()
        self.card_pairs = []


class PlayerHand(ttk.Frame):
    TOO_MANY_CARDS = 6
    OVERFLOW_COEFF = 3
    MIN_PADDING = -CARD_WIDTH / 2

    def __init__(self, parent, hand, options, callback, shown=True):
        self.padding = 6
        width = self.calculate_width(hand)
        height = CARD_HEIGHT + self.padding * 2
        ttk.Frame.__init__(self, parent, width=width, height=height)
        self.hand = hand
        self.shown = shown
        self.callback = callback

        self.update_hand(hand, options)

    def calculate_width(self, hand):
        padding = self.padding
        if len(hand) > self.TOO_MANY_CARDS:
            cards_over = len(hand) - self.TOO_MANY_CARDS
            padding -= self.OVERFLOW_COEFF * cards_over
            padding = max(padding, self.MIN_PADDING)
            return (CARD_WIDTH + padding) * (len(hand) + 1) + self.padding
        else:
            return (CARD_WIDTH + self.padding) * len(hand)

    def update_hand(self, hand, options):
        padding = self.padding
        if len(hand) > self.TOO_MANY_CARDS:
            cards_over = len(hand) - self.TOO_MANY_CARDS
            padding -= self.OVERFLOW_COEFF * cards_over
            padding = max(padding, self.MIN_PADDING)
            for i, card in enumerate(hand):
                playing_card = InteractablePlayingCard(
                    self, card, i, card in options, self.callback) \
                    if self.shown else BlankCardFrame(self)
                playing_card.place(x=(CARD_WIDTH + padding) * i, y=0,
                                   anchor="nw")
        else:
            for i, card in enumerate(hand):
                playing_card = InteractablePlayingCard(
                    self, card, i, card in options, self.callback) \
                    if self.shown else BlankCardFrame(self)
                playing_card.place(x=(CARD_WIDTH + padding) * i, y=0,
                                   anchor="nw")


class GuiState(State):
    def __init__(self, players_list, deck, pile=None, table=None,
                 status=None, gui_needed=False):
        self.trump_card = deck.get_trump()
        self.pointer = Pointer(players_list, self.trump_card.suit)
        super().__init__(players_list, self.pointer, deck, self.trump_card,
                         pile, table, status)

        self.gui_needed = gui_needed
        self.draw_cards()


class GuiStateWithHuman(GuiState):
    def __init__(self, players_list, deck, pile=None, table=None,
                 status=None, gui_needed=False):
        super().__init__(players_list, deck, pile, table, status, gui_needed)
        self.human_player = \
            self.attacker if self.attacker.human else self.defender
        self.attacking = self.attacker.human
        self.count = 0
        self.state_over = False
        self.status = "Attacking" if self.attacking else "Defending"
        self.gui_helper()

    def gui_helper(self):
        if self.check_win():
            print(self.status)
            gui.winner_decided(self.status)
            return self.status
        if not self.attacker.human:
            self.attacker.attack(self)
        gui.build_gui(self, self.card_pick_callback, self.status,
                      is_attacker_first_state=self.attacking)

    def gui_first_stage(self, choice, card):
        if self.attacking:
            self.current_player = self.attacker
            self.table.add_single_card(card)
            self.attacker.remove_card(card)
            self.current_player = self.defender
            if self.defender.defend(self) is None:
                self.defender.grab_table(self.table)
        else:
            self.current_player = self.defender
            if choice is None:
                self.attacker.draw_cards(self.deck)
                self.defender.grab_table(self.table)
                self.state_over = True
            else:
                self.table.add_single_card(card)
                self.defender.remove_card(card)
            self.current_player = self.attacker
            self.attacker.attack(self)
        self.count += 1

    def gui_update_players(self):
        self.swap_players()
        self.status = "Attacking" if self.attacking else "Defending"

    def second_stage_reset_state(self):
        self.state_over = True
        print('_second_stage no options for attacker')
        self.draw_cards()
        self.pile.update(self.table)
        self.table.clear_cards()
        self.gui_update_players()

    def second_stage_attacking(self, choice, card):
        self.current_player = self.attacker
        if choice is None:
            self.second_stage_reset_state()
            self.attacker.attack(self)
        else:
            self.table.add_single_card(card)
            self.attacker.remove_card(card)
            self.count += 1
            if self.defender.defend(self) is None:
                self.attacker.draw_cards(self.deck)
                self.state_over = True

    def second_stage_defending(self, choice, card):
        self.current_player = self.defender
        if choice is None:
            self.defender.grab_table(self.table)
            self.draw_cards()
            gui.update_gui(self, self.card_pick_callback, self.status)
            if not self.check_win():
                self.count = 0
                self.attacker.attack(self)
            gui.update_gui(self, self.card_pick_callback, self.status)
            return
        else:
            self.defender.remove_card(card)
            self.table.add_single_card(card)
        self.current_player = self.attacker
        if self.attacker.add_card(self) is not None:
            self.count += 1
            gui.update_gui(self, self.card_pick_callback, self.status)
            if self.check_win():
                gui.winner_decided(self.status)
            return
        else:
            self.second_stage_reset_state()
            gui.update_gui(self, self.card_pick_callback, self.status,
                           is_attacker_first_state=True)
            if self.check_win():
                gui.winner_decided(self.status)
                return
            return False

    def second_stage_state_over(self, choice):
        if choice is None:
            self.defender.grab_table(self.table)
        else:
            self.pile.update(self.table)
        self.draw_cards()
        self.table.clear_cards()
        self.gui_update_players()
        self.count = 0

    def card_pick_callback(self, choice, card):
        if self.check_win():
            gui.winner_decided(self.status)
            return
        if self.state_over:
            self.count = 0
            self.state_over = False
        if self.count == 0:
            self.gui_first_stage(choice, card)
        elif 1 <= self.count < 6:  # Second stage.
            if self.attacking:
                self.second_stage_attacking(choice, card)
            else:
                return self.second_stage_defending(choice, card)
        else:
            self.second_stage_state_over(choice)
        if self.check_win():
            gui.winner_decided(self.status)
            return
        gui.update_gui(self, self.card_pick_callback, self.status)


class guiStateWithAI(GuiState):
    def __init__(self, players_list, deck, pile=None, table=None,
                 status=None, gui_needed=False):
        super().__init__(players_list, deck, pile, table, status, gui_needed)
        self.status = ""
        self.player_won = False
        self.current_player = self.attacker
        if gui_needed:
            gui.build_gui(self, None, self.status, True)
            self.gui_helper()

    def gui_helper(self):
        gui.update_gui(self, None, self.status, True)
        if self.check_win():
            print(self.status)
            gui.winner_decided(self.status)
            return self.status
        if self.gui_first_stage() == True:
            gui.update_gui(self, None, self.status, True)
            self.gui_helper()
            return "first_stage_finish"
        gui.update_gui(self, None, self.status, True)
        self.gui_second_stage()
        self.gui_helper()

    def gui_first_stage(self):
        print(self.trump_card)
        print(self.attacker.nickname, 'num cards',
              len(self.attacker.get_cards()))
        print(self.defender.nickname, 'defender num cards',
              len(self.defender.get_cards()))
        print('deck num cards', len(self.deck.get_cards()))
        self.current_player = self.attacker
        if self.attacker.attack(self) is None:
            self.pile.update(self.table)
            self.table.clear_cards()
            self.draw_cards()
            self.swap_players()
            self.gui_first_stage()
            return
        # defender can't defend
        self.current_player = self.defender
        if self.defender.defend(self) is None:
            print('_first_stage no options for defender')
            self.attacker.draw_cards(self.deck)
            return True
        # defender defended successfully
        return False

    def gui_second_stage(self):
        cnt = 1
        while True and cnt < 6:
            gui.update_gui(self, None, self.status, True)
            self.current_player = self.attacker
            if self.attacker.add_card(self) is not None:
                cnt += 1
                self.current_player = self.defender
                if self.defender.defend(self) is None:
                    print('_second_stage no options for defender')
                    return False
            else:
                print('_second_stage no options for attacker')
                self.attacker.draw_cards(self.deck)
                self.defender.draw_cards(self.deck)
                self.pile.update(self.table)
                self.table.clear_cards()
                self.swap_players()
                gui.update_gui(self, None, self.status, True)
                return False
        print("No more attacking allowed, moving to the next state!")
        self.attacker.draw_cards(self.deck)
        self.defender.draw_cards(self.deck)


class DurakGame:
    def __init__(self, players_list, gui=None):
        self.deck = Deck([])
        self.player_list = players_list
        self.pile = Pile([])
        self.gui = gui
        self.is_human_playing = False
        for player in players_list:
            if player.human:
                self.is_human_playing = True
        self.curr_state = None
        if self.gui is not None:
            self.gui_helper()

    def gui_helper(self):
        if self.is_human_playing:
            self.curr_state = GuiStateWithHuman(
                self.player_list, self.deck, self.pile, gui_needed=True)
        else:
            self.curr_state = guiStateWithAI(
                self.player_list, self.deck, self.pile, gui_needed=True)


class Durak_GUI(tk.Tk):
    BASE_AMOUNT_OF_GAMES = 50

    def __init__(self, players_list, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "Durak")

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.player_list = players_list

        self.winners = []
        self.amount_of_games = 0
        self.amount_of_games_won = 0
        self.stop_at = self.BASE_AMOUNT_OF_GAMES

        self.after(0, func=self.start_game)

    def start_game(self):
        for player in self.player_list:
            player.clear_cards()
        self.game = DurakGame(self.player_list, self)

    def winner_decided(self, nickname):
        self.winners.append(nickname)

        self.amount_of_games += 1
        self.amount_of_games_won += 1 if nickname == \
                                         self.player_list[1].nickname else 0

        self.container.destroy()
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)

        if self.amount_of_games < self.stop_at:
            self.after(0, func=self.start_game)
        else:
            print("Player 2 win rate:",
                  self.amount_of_games_won / self.amount_of_games)
            self.stop_at += self.BASE_AMOUNT_OF_GAMES

        win_text = nickname + " has won " + \
                   str(self.amount_of_games_won / self.amount_of_games
                       if nickname == self.player_list[1].nickname
                       else 1 -
                            self.amount_of_games_won / self.amount_of_games) + \
                   " of the games"
        self.winner_label = ttk.Label(self.container,
                                      text=win_text,
                                      font=('Helvetica', 25))
        self.winner_label.pack()

        self.replay_button = ttk.Button(self.container,
                                        text="Run again, compound results",
                                        command=self.start_game)
        self.replay_button.pack()

    def update_gui(self, game, choose_card_callback, status, show_all=False,
                   is_attacker_first_state=False):
        self.enemy_player_hand.destroy()
        self.enemy_player_hand = PlayerHand(self.container,
                                            self.player_list[0].get_cards(), [],
                                            choose_card_callback,
                                            shown=show_all)
        self.enemy_player_hand.grid(row=0, column=1)

        progress_text = "Games played so far: " + str(
            self.amount_of_games) + "\nWin rate: " + \
                        str(self.amount_of_games_won / self.amount_of_games if
                            self.amount_of_games != 0 else 0)
        self.progress_label.configure(text=progress_text)

        self.attacking_label.configure(text=status)

        self.table.reset_table()
        for i in range(0, len(game.table.get_cards()), 2):
            pair = CardPair(self.table)
            bottom_card = PlayingCardFrame(pair, game.table.get_cards()[i])
            pair.set_bottom_card(bottom_card)
            if i + 1 < len(game.table.get_cards()):
                top_card = PlayingCardFrame(pair, game.table.get_cards()[i + 1])
                pair.set_top_card(top_card)
            self.table.add_card_pair(pair)
        self.table.update_view()

        self.deck.destroy()
        self.deck = DeckFrame(self.container, len(game.deck.get_cards()))
        self.deck.grid(row=1, column=2)

        playable_cards = self.player_list[1].options(game.table,
                                                     game.trump_card.suit)
        self.player_hand.destroy()
        self.player_hand = PlayerHand(self.container,
                                      self.player_list[1].get_cards(),
                                      playable_cards, choose_card_callback,
                                      shown=True)
        self.player_hand.grid(row=2, column=1)

        if not is_attacker_first_state:
            self.admit_defeat.grid(row=2, column=2)
        else:
            self.admit_defeat.grid_forget()
        tk.Tk.update(self)

    def build_gui(self, game, choose_card_callback, status, show_all=False,
                  is_attacker_first_state=False):
        if self.container is not None:
            self.container.destroy()
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)

        self.enemy_label = ttk.Label(self.container,
                                     text=self.player_list[0].nickname)
        self.enemy_label.grid(row=0, column=0)

        self.enemy_player_hand = PlayerHand(self.container,
                                            self.player_list[0].get_cards(), [],
                                            choose_card_callback,
                                            shown=show_all)
        self.enemy_player_hand.grid(row=0, column=1)

        progress_text = "Games played so far: " + str(self.amount_of_games)
        self.progress_label = ttk.Label(self.container, text=progress_text,
                                        font=('Helvetica', 15))
        self.progress_label.grid(row=0, column=2)

        self.attacking_label = ttk.Label(self.container, text=status)
        self.attacking_label.grid(row=1, column=0)

        self.table = TableFrame(self.container)
        self.table.grid(row=1, column=1)

        for i in range(0, len(game.table.get_cards()), 2):
            pair = CardPair(self.table)
            bottom_card = PlayingCardFrame(pair, game.table.get_cards()[i])
            pair.set_bottom_card(bottom_card)
            if i + 1 < len(game.table.get_cards()):
                top_card = PlayingCardFrame(pair, game.table.get_cards()[i + 1])
                pair.set_top_card(top_card)
            self.table.add_card_pair(pair)
        self.table.update_view()

        self.deck = DeckFrame(self.container, len(game.deck.get_cards()))
        self.deck.grid(row=1, column=2)

        self.trump_card = PlayingCardFrame(self.container, game.trump_card)
        self.trump_card.grid(row=1, column=3)

        self.player_label = ttk.Label(self.container,
                                      text=self.player_list[1].nickname)
        self.player_label.grid(row=2, column=0)

        playable_cards = self.player_list[1].options(game.table,
                                                     game.trump_card.suit)
        self.player_hand = PlayerHand(self.container,
                                      self.player_list[1].get_cards(),
                                      playable_cards, choose_card_callback,
                                      shown=True)
        self.player_hand.grid(row=2, column=1)

        self.admit_defeat = ttk.Button(self.container, text="Forfeit state",
                                       command=lambda: choose_card_callback(
                                           None, None))
        self.admit_defeat.grid(row=2, column=2)
        if is_attacker_first_state:
            self.admit_defeat.grid_forget()
        tk.Tk.update(self)


human = HumanPlayer("Eva")
p1 = None
p2 = PureQlearningPlayer(p1, "PureQlearningPlayer")
p1 = SimpleMinmaxPlayer(p2, "SimpleMinmaxPlayer")
p3 = SimplePlayer()

# gui = Durak_GUI([p1, p2], None)
gui = Durak_GUI([p3, human], None)


if __name__ == "__main__":
    gui.mainloop()
