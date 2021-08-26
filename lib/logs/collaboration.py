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
# jva_vals is a dictionary with Block objects (minecraft_block.py) as keys and the heat level as values
def jva(target_blocks_dct):
    jva_vals = {}

    # puts all the given target blocks in a dictionary with its heat level as 3
    for block_dct in target_blocks_dct.values():
        x = block_dct["x"]
        y = block_dct["y"]
        z = block_dct["z"]

        target_block = Block(x, y, z)   # Block object
        jva_vals[target_block] = jva_vals.get(target_block, 0) + 3

        jva_vals = nearby_blocks(jva_vals, target_block, 1)
        jva_vals = nearby_blocks(jva_vals, target_block, 2)

    return jva_vals


# takes jva_vals from the jva() function above, a target block, and an offset
# for each block within the offset of the given target block, that block's heat level will be updated
# heat level is 0 for blocks outside the offset
# heat level increase is 2 for blocks with offset 1
# heat level increase is 1 for blocks with offset 2
def nearby_blocks(jva_vals, target_block, offset):
    level_add = 0
    if offset == 1:
        level_add = 2
    elif offset == 2:
        level_add = 1

    x = target_block.x
    y = target_block.y
    z = target_block.z

    x_minus = x - offset    # min x value for block in offset
    x_plus = x + offset     # max x value
    y_minus = y - offset    # min y value for block in offset
    y_plus = y + offset     # max y value
    z_minus = z - offset    # min z value
    z_plus = z + offset     # max z value

    # add the heat level (level_add) to the block's preexisting heat level
    one_block_face(level_add, x_minus, x_minus, y_minus, y_plus, z_minus, z_plus)   # 1st side
    one_block_face(level_add, x_plus, x_plus, y_minus, y_plus, z_minus, z_plus)     # 2nd side
    one_block_face(level_add, x_minus, x_plus, y_minus, y_minus, z_minus, z_plus)   # 3rd side
    one_block_face(level_add, x_minus, x_plus, y_plus, y_plus, z_minus, z_plus)     # 4th side
    one_block_face(level_add, x_minus, x_plus, y_minus, y_plus, z_minus, z_minus)   # 5th side
    one_block_face(level_add, x_minus, x_plus, y_minus, y_plus, z_plus, z_plus)     # 6th side

    return jva_vals


# if you imagine all the blocks as a hollow Rubik's cube, we're looking at one side in this function
# this is the function that should modify heat levels
def one_block_face(level_add, x_min, x_max, y_min, y_max, z_min, z_max):
    if x_min == x_max:
        make_2d_array(y_min, y_max, z_min, z_max, x_min)
    elif y_min == y_max:
        make_2d_array(x_min, x_max, z_min, z_max, y_min)
    elif z_min == z_max:
        make_2d_array(x_min, x_max, y_min, y_max, z_min)
    return ":)"


# this function constructs a data structure representation of one side of the hollow Rubik's cube
# min1 and max1 are the constraints in one dimension
# min2 and max2 are the constraints in the other dimension
# pos is a single int (i.e. if using this function for the side that has z=z_min, then min1=x_min, max1=x_max,
#                       min2=y_min, max2=y_max, and pos=z_min)
def make_2d_array(min1, max1, min2, max2, pos):
    retval = []
    for i in range(min1, max1+1):
        for j in range(min2, max2+1):
            print("tbd")
    return retval
