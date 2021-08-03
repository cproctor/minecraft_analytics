import pandas as pd
import collaboration
import selection


def main():
    filename = '../../data/df/production.csv'
    dataframe = pd.read_csv(filename)

    # print(dataframe)
    file_excerpt = "../../data/minecraft_replay_recordings/2021_07_07_Workshop_1.mcpr"
    selection.slice_excerpt(file_excerpt, '00:00:04', '00:01:03', 'test')


if __name__ == '__main__':
    main()
