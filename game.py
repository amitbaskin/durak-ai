# import logging
# import os
from game_mechanics import *
from durak_ai import SmartPlayer, SmartPlayer2
# from player import HumanPlayer


class Game:
    def __init__(self, players_list):
        self.players_list = players_list

#
# # p1 = AiPlayerDumb()
# p2 = SimplePlayer()
p2 = None
p3 = SmartPlayer2(p2, " one")
p2 = SmartPlayer2(p3, " two")
p4 = None
p5 = SmartPlayer(p4, " one")
p4 = SmartPlayer(p5, " two")
# # players_list = [p1, p2]
smart_players_2_list = [p2, p3]
smart_players_list = [p4, p5]



def game_instance(list_of_players):
    win_count = 0
    for _ in range(1000):
        for player in list_of_players:
            player._refresh()
        deck = Deck()
        print(deck)
        g = GameProcess(list_of_players, deck)
        # ptr = Pointer(list_of_players)
        if g.play() == list_of_players[1].nickname:
            win_count += 1

    print("Player 2 win rate:", win_count / 1000)


# # print(game_instance(players_list))
# print(game_instance(smart_players_2_list))
print(game_instance(smart_players_list))
