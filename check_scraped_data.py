"""A Python script containing functions to verify that data scraping was correctly done."""

import pandas as pd
import os

from pathlib import Path
from typing import Tuple, List


def check_round_names(results_dfs: List[pd.DataFrame], motions_dfs: List[pd.DataFrame]) -> bool:
    for i in range(len(results_dfs)):
        results_df, motions_df = results_dfs[i], motions_dfs[i]
        results_round_names = set(results_df['Round Name'])
        motions_round_names = set(results_df['Round Name'])
        if not motions_round_names.issubset(results_round_names):
            return False
    return True


def get_dfs(folder: str) -> Tuple[List[pd.DataFrame], List[pd.DataFrame], List[pd.DataFrame]]:
    results_dfs, speakers_dfs, motions_dfs = [], [], []

    for file in os.listdir(folder):  # iterate through all the scraped data
        # find the file's filepath and get the dataframe
        filepath = Path(folder + file)

        if file[-14:] == ' - Results.csv':  # if results file
            df = pd.read_csv(filepath)
            results_dfs.append(df)
        elif file[-14:] == ' - Motions.csv':
            df = pd.read_csv(filepath)
            motions_dfs.append(df)
        elif file[-15:] == ' - Speakers.csv':
            df = pd.read_csv(filepath)
            speakers_dfs.append(df)
        else:  # something's wrong
            print(file)

    return results_dfs, speakers_dfs, motions_dfs


if __name__ == '__main__':
    results_dfs, speakers_dfs, motions_dfs = get_dfs('scraped_data/')
    print(check_round_names(results_dfs, motions_dfs))
