import logging
import os
from game_mechanics import *
from durak_ai import *
from player import HumanPlayer


class Game:
    def __init__(self, players_list):
        self.players_list = players_list


p1 = AiPlayerDumb('WALL E')
p2 = SimplePlayer('EVA')
players_list = [p1, p2]

if os.path.isfile('game.log'):
    os.remove('game.log')


logger = logging.getLogger('logging_games')
logger.setLevel(logging.INFO)
fh = logging.FileHandler('game.log')
logger.addHandler(fh)
logger.info({'Game' : 0})


def game_instance(list_of_players, logger=None):
    win_count = 0
    for _ in range(100000):
        for player in list_of_players:
            player._refresh()
        deck = Deck()
        print(deck)
        g = GameProcess(list_of_players, deck, logger)
        # ptr = Pointer(list_of_players)
        if g.play() == list_of_players[1].nickname:
            win_count += 1

    print("Player 2 win rate:", win_count / 100000)


print(game_instance(players_list, logger))
