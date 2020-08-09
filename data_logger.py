import logging
import time
import os
from DurakAi import RandomPlayer
from Game import game_instance

if os.path.isfile('game.log'):
    os.remove('game.log')

logger = logging.getLogger('logging_games')
logger.setLevel(logging.INFO)
fh = logging.FileHandler('game.log')

P1 = RandomPlayer('WALL E')
P2 = RandomPlayer('EVA')
players_list = [P1, P2]
i = 0
t = time.time()
logger.addHandler(fh)
logger.info({'Game' : 0})

while i != 3:
    print(game_instance(players_list, logger))
    print(P1.cards)
    print(P2.cards)
    i += 1
    logger.info({"Game" : i})
    print(i)
    print(time.time() - t)
