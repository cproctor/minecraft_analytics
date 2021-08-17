# Functions related to analysis of collaboration between players

import pandas as pd
from selection import filter_df
from minecraft_block import Block


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


# target_blocks_dct format: {"player_name": {"x": x, "y": y, "z": z}}
# jva_vals is a dictionary with Block objects (minecraft_block.py) as keys and the level as values
def jva(target_blocks_dct):
    jva_vals = {}

    for block_dct in target_blocks_dct.values():
        x = block_dct["x"]
        y = block_dct["y"]
        z = block_dct["z"]

        target_block = Block(x, y, z)   # Block object
        jva_vals[target_block] = jva_vals.get(target_block, 0) + 3

        jva_vals = nearby_blocks(jva_vals, target_block, 1)
        jva_vals = nearby_blocks(jva_vals, target_block, 2)

    return jva_vals


def nearby_blocks(dct, block, offset):
    num_blocks = 0
    level_add = 0
    if offset == 1:
        num_blocks = 26     # a 3x3 empty cube is made up of 26 blocks
        level_add = 2
    if offset == 2:
        num_blocks = 98     # a 5x5 empty cube is made up of 98 blocks
        level_add = 1

    x = block.x
    y = block.y
    z = block.z
    for n in range(num_blocks):
        print()

    return dct
