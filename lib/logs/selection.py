# Functions related to selecting and filtering analysis dataframes

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

