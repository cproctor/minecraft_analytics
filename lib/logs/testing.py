import pandas as pd
import collaboration
import selection


def main():
    filename = '../../data/df/production.csv'
    dataframe = pd.read_csv(filename)

    # print(dataframe)
    file_excerpt1 = "../../data/minecraft_replay_recordings/2021_07_07_Workshop_1.mcpr"
    file_excerpt2 = "../../data/minecraft_audio_recordings/2021_07_14_workshop_2_zoom.mp4"
    selection.slice_excerpt(file_excerpt2, '00:05:04', '00:01:03', 'test')


if __name__ == '__main__':
    main()
