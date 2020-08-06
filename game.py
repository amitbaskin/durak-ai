# import logging
# import os
from game_mechanics import *
from durak_ai import SmartPlayer, SmartPlayer2, SimplePlayer, PureQAgent
import pickle
import sys
import os
# from player import HumanPlayer
import re

def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)


class Game:
    def __init__(self, players_list):
        self.players_list = players_list

#
# # p1 = AiPlayerDumb()
# # p2 = SimplePlayer()
# p2 = None
# p3 = SmartPlayer2(p2, " one")
# p2 = SmartPlayer2(p3, " two")
# p4 = None
# p5 = SmartPlayer(p4, " one")
# p4 = SmartPlayer(p5, " two")
# # players_list = [p1, p2]
# smart_players_2_list = [p2, p3]
# smart_players_list = [p4, p5]
# # p6 = None
# p7 = SimplePlayer()
# p6 = PureQAgent(p7, " two")
# mixed_smart_list = [p6, p7]


def remove_zero_items(weights):
    return dict(filter(lambda x: x[1] != 0, weights.items()))


def get_epoch_num(prefix):
    weight_files = [file for file in os.listdir("pickle") if file.startswith(prefix)]
    if len(weight_files) == 0:
        return 0
    weight_file = natural_sort(weight_files)[-2]
    return int(weight_file.split("_")[2])


def train_approx_q_agent(versus_player):
    sys.stdout = open('log.txt', 'w')
    sys.stderr = open('log_err.txt', 'w')
    agent = PureQAgent(versus_player, "")
    list_of_players = [agent, versus_player]

    start = get_epoch_num("trained_weights_")
    for i in range(start + 1, start + 101):
        num_won = 0
        for _ in range(100):
            for player in list_of_players:
                player._refresh()
            deck = Deck([])
            g = GameProcess(list_of_players, deck)
            if g.play() == agent.nickname:
                num_won += 1

        trained_weights = remove_zero_items(agent.qAgent.weights)
        path = os.path.join("pickle", 'trained_weights_{}_epoch.pickle'.format(i))
        with open(path, 'wb') as handle:
            pickle.dump(trained_weights, handle)
        path = os.path.join("pickle", 'trained_weights_latest.pickle'.format(i))
        with open(path, 'wb') as handle:
            pickle.dump(trained_weights, handle)

        num_non_zero = sum([1 for w in trained_weights.values() if w != 0])
        with open('approxQAgent_learn_stats.txt', 'a') as handle:
            handle.write("{} with win rate of {}\n".format(num_non_zero, round(num_won / 100, 2)))


def train_q_agent(versus_player):
    sys.stdout = open('log.txt', 'w')
    sys.stderr = open('log_err.txt', 'w')
    agent = PureQAgent(versus_player, "", False)
    list_of_players = [agent, versus_player]

    start = get_epoch_num("trained_q_values_")
    for i in range(start + 1, start + 101):
        num_won = 0
        for _ in range(100):
            for player in list_of_players:
                player._refresh()
            deck = Deck([])
            g = GameProcess(list_of_players, deck)
            if g.play() == agent.nickname:
                num_won += 1

        trained_q_values = remove_zero_items(agent.qAgent.q_values)
        path = os.path.join("pickle", 'trained_q_values_{}_epoch.pickle'.format(i))
        with open(path, 'wb') as handle:
            pickle.dump(trained_q_values, handle)
        path = os.path.join("pickle", 'trained_q_values_latest.pickle'.format(i))
        with open(path, 'wb') as handle:
            pickle.dump(trained_q_values, handle)

        num_non_zero = sum([1 for w in trained_q_values.values() if w != 0])
        with open('qAgent_learn_stats.txt', 'a') as handle:
            handle.write("{} with win rate of {}\n".format(num_non_zero, round(num_won / 100, 2)))


def game_instance(list_of_players):
    for player in list_of_players:
        player._refresh()
    deck = Deck([])
    g = GameProcess(list_of_players, deck)
    g.play()


# # print(game_instance(players_list))
# print(game_instance(smart_players_2_list))
# print(game_instance(smart_players_list))
# print(game_instance(mixed_smart_list))

train_approx_q_agent(SimplePlayer())
