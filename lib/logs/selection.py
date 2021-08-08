# Functions related to selecting and filtering analysis dataframes

import pandas as pd
import ffmpy
import sys


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


# creates an excerpt of a file at the given timestamp
# start/length time format: HH:MM:SS.xxx
def slice_excerpt(input_filepath, start_time, length, label):
    # get the name of the file minus the path
    input_filename = input_filepath.split('/').pop()

    # get the name of the file separated from the extension
    output = input_filename.split('.')
    # create a new file path with a descriptive label
    output_filepath = output[0] + '_' + label + '.' + output[1]

    # find the location of ffmpeg.exe on your machine and edit this variable to match
    ffmpeg_executable = 'C:\\Users\\ikond\\AppData\\Roaming\\.minecraft\\ffmpeg-4.4-essentials_build\\bin\\ffmpeg.exe'

    # constructs the ffmpeg command
    ff = ffmpy.FFmpeg(
        executable=ffmpeg_executable,
        inputs={input_filepath: '-ss ' + start_time},
        outputs={output_filepath: '-t ' + length + ' -c copy'}
    )

    try:
        ff.run()
    except ffmpy.FFRuntimeError:
        sys.stderr.write("The label " + label + " is already taken for this file.")
        sys.stderr.write(" Please choose something else or delete " + output_filepath + ".")
