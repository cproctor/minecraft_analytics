# Functions related to analysis of collaboration between players

import pandas as pd


def filter_df(df, start_time, stop_time, players, events):
    new = df
    if (start_time != None):
        new = new[(new.index >= start_time)]
    if (stop_time != None):
        new = new[(new.index <= stop_time)]
    if (players != None):
        new = new[new['player'].isin(players)]
    if (events != None):
        new = new[new['event'].isin(events)]
    return new


def dist(player_moves, player_0, player_0_location, player_1, player_1_location):
    if (player_moves['player'] == player_0):
        player_0_location[0] = player_moves['location_x']
        player_0_location[1] = player_moves['location_y']
        player_0_location[2] = player_moves['location_z']
    if (player_moves['player'] == player_1):
        player_1_location[0] = player_moves['location_x']
        player_1_location[1] = player_moves['location_y']
        player_1_location[2] = player_moves['location_z']
    if ((None not in player_0_location) and (None not in player_1_location)):
        distance = (((player_0_location[0] - player_1_location[0]) ** 2) + (
                (player_0_location[1] - player_1_location[1]) ** 2) + (
                            (player_0_location[2] - player_1_location[2]) ** 2)) ** 0.5
        return distance


def player_distance(df, player_0, player_1):
    player_moves = filter_df(df, None, None, [player_0, player_1], None)  # or ['PlayerMoveEvent']
    player_0_location = [None, None, None]
    player_1_location = [None, None, None]
    player_moves['dist'] = player_moves.apply(
        lambda x: dist(x, player_0, player_0_location, player_1, player_1_location), axis=1)
    return player_moves


def main():
    filename = '../data/df/production.csv'
    dataframe = pd.read_csv(filename)

    print(dataframe)


if __name__ == '__main__':
    main()
