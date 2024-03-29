import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np

COORDS = ['x', 'y', 'z']
ANGLES = ['pitch', 'yaw']

def get_location_gaze(df, players):
    """Converts a normalized logs df to a df with position and gaze columns
    for each player. Index is timestamps of the union of all player events.
    """
    cols = (
        ['location_' + c for c in COORDS] + 
        ['eye_location_' + c for c in COORDS] + 
        ['target_block_' + c for c in COORDS] + 
        ['eye_direction_' + a for a in ANGLES]
    )
    dfs = []
    for player in players:
        player_df = df[df.player == player]
        player_col_names = {col: player + '_' + col for col in cols}
        player_df = player_df.rename(columns=player_col_names)
        dfs.append(player_df[player_col_names.values()])
    lgdf = pd.concat(dfs).sort_index()
    lgdf = lgdf.ffill().dropna()
    return lgdf

def distance_measure(df, key_a, key_b, location):
    """Computes the squared distance between two players for a given location.
    df should be in lgdf form. key_a and key_b refer to players; 
    location may be 'location', 'eye_location', or 'target_block'.
    """
    def cols(key, loc):
        return [key + '_' + loc + '_' + c for c in COORDS]
    ax, ay, az = cols(key_a, location)
    bx, by, bz = cols(key_b, location)
    return (df[bx]-df[ax])**2 + (df[by]-df[ay])**2 + (df[bz]-df[az])**2

def joint_attention_schneider_pea_2013(df, key_a, key_b, distance_threshold=10, window_seconds=2):
    """Computes Schneider & Pea's (2013, p. 111) binary metric of joint attention.
    Distance threshold is the maximum euclidian distance between players' target blocks.
    Uses default 2 seconds for time window, following Schneider & Pea's reference to 
    Richardson & Dale, 2005. 
    """
    dist = distance_measure(df, key_a, key_b, 'target_block')
    joint = dist ** 2 <= distance_threshold # CP note (2023-01-20) Why is dist squared?
    windows = joint.rolling(str(window_seconds)+'s')
    return windows.max().astype(bool)

def plot_boolean_joint_attention(df, colors=None):
    """Plots boolean values; returns figure
    """
    if colors is None:
        colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    date_format = mdates.DateFormatter('%H:%M')
    fig, ax = plt.subplots(figsize=(6, 2))
    ax.xaxis.set_major_formatter(date_format)
    #fig.autofmt_xdate()
    for col, color in zip(df.columns, colors):
        times = df[df[col]].index
        ax.scatter(x=times, y=[col] * len(times), marker='s', color=color)
    return fig
