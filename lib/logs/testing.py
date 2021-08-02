import pandas as pd
import collaboration
import selection


def main():
    filename = '../../data/df/production.csv'
    dataframe = pd.read_csv(filename)

    print(dataframe)


if __name__ == '__main__':
    main()
