import logging
import os
from game_mechanics import *
from durak_ai import *
from player import HumanPlayer


class Game:
    def __init__(self, players_list):
        self.players_list = players_list


p1 = AiPlayerDumb()
p2 = SimplePlayer()
players_list = [p1, p2]

def game_instance(list_of_players):
    win_count = 0
    for _ in range(100000):
        for player in list_of_players:
            player._refresh()
        deck = Deck()
        print(deck)
        g = GameProcess(list_of_players, deck)
        # ptr = Pointer(list_of_players)
        if g.play() == list_of_players[1].nickname:
            win_count += 1

    print("Player 2 win rate:", win_count / 100000)


print(game_instance(players_list))
