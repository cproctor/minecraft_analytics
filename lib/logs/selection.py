# Functions related to selecting and filtering analysis dataframes

import pandas as pd
import ffmpy


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


# start/length time format: HH:MM:SS.xxx
def slice_excerpt(input_filepath, start_time, length, label):
    # get the name of the file minus the path
    input_filename = input_filepath.split('/').pop()
    print(input_filename)

    # get the name of the file minus the extension
    output = input_filename.split('.')
    # create a new file path with a descriptive label
    output_filepath = output[0] + '_' + label + '.' + output[1]
    print(output_filepath)

    # constructs the ffmpeg command
    ff = ffmpy.FFmpeg(
        inputs={input_filepath: '-ss ' + start_time},
        outputs={output_filepath: '-t ' + length + ' -c copy'}
    )
    print(ff.cmd)
    # ff.run()
