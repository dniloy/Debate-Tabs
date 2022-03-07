"""Analyzes results files for data."""
import pandas as pd
import os
import re
import validators

from pathlib import Path
from typing import List, Tuple, Set


def team_positions_stats(results_dfs: List[pd.DataFrame]) -> Tuple[tuple, tuple, tuple]:
    two_teams_positions_list = [0, 0]  # list for two-team formats e.g. Australs
    four_teams_positions_list = [0, 0, 0, 0]  # list for four-team formats e.g. BP

    for results_df in results_dfs:  # for each results dataframe
        for index, row in results_df.iterrows():  # for every room in the file

            room = row['Rankings']
            teams = room.split('\', \'')  # split teams by commas
            teams[0] = teams[0][2:]  # remove the [' at the start
            teams[-1] = teams[-1][:-2]  # remove the '] at the end
            for team in teams:  # for each team in the room
                # find team position substring
                position = re.search(r'\([A-Z]+\)', team[-4:]).group()
                # add the score in team[0] to the appropriate list slot
                if position in {'(P)', '(G)', '(A)'}:
                    two_teams_positions_list[0] += int(team[0])
                elif position in {'(O)', '(N)'}:
                    two_teams_positions_list[1] += int(team[0])
                elif position == '(OG)':
                    four_teams_positions_list[0] += int(team[0])
                elif position == '(OO)':
                    four_teams_positions_list[1] += int(team[0])
                elif position == '(CG)':
                    four_teams_positions_list[2] += int(team[0])
                elif position == '(CO)':
                    four_teams_positions_list[3] += int(team[0])
                else:
                    print(position)

    if two_teams_positions_list == [0, 0]:
        two_teams_positions_list = []
    if four_teams_positions_list == [0, 0, 0, 0]:
        four_teams_positions_list = []

    # get average team position scores for two team format
    normalized_two = [score * 3 / (two_teams_positions_list[0] + two_teams_positions_list[1])
                      for score in two_teams_positions_list]
    # get average team position scores for four team format
    normalized_four = [score * 6 / (four_teams_positions_list[0] + four_teams_positions_list[1] +
                                    four_teams_positions_list[2] + four_teams_positions_list[3])
                       for score in four_teams_positions_list]
    # get average side scores for four team format
    normalized_bp_two = [(normalized_four[0] + normalized_four[2]) / 2,
                         (normalized_four[1] + normalized_four[3]) / 2]

    return tuple(normalized_two), tuple(normalized_four), tuple(normalized_bp_two)


def round_by_round_stats(results_dfs: List[pd.DataFrame]) -> List[tuple]:
    rounds_stats = []
    for round in results_dfs:
        rounds_stats.append(team_positions_stats([round]))
    return rounds_stats


def unique_round_names(results_dfs: List[pd.DataFrame]) -> Set[str]:
    # get filepath for scraped data directory
    unique_round_names = set()

    for results_df in results_dfs:
        # if finals round
        names = {round for round in results_df['Round Name']
                 if ('nal' in round or " GF" in round or 'emi' in round)}
        # unique_round_names = unique_round_names.union(set(results_df['Round Name']))
        unique_round_names = unique_round_names.union(names)

    return unique_round_names


def count_debates(results_dfs: List[pd.DataFrame]) -> int:
    """Count total number of debates in the given folder.

    Preconditions
        - folder starts without '/' and ends with '/'"""
    # find folder containing debates data
    debate_count = 0

    for results_df in results_dfs:  # for every file in the given folder
        debate_count += len(results_df['Rankings'])  # add number of rooms to debate_count
    return debate_count


def get_results_dfs(folder: str) -> List[pd.DataFrame]:
    results_dfs = []

    for file in os.listdir(folder):  # iterate through all the scraped data
        if file[-14:] == ' - Results.csv':  # if results file
            # find the file's filepath and get the dataframe
            filepath = Path(folder + file)
            results_df = pd.read_csv(filepath)
            results_dfs.append(results_df)

    return results_dfs


def get_finals_rankings_dfs(results_dfs: List[pd.DataFrame]) -> List[pd.DataFrame]:
    outrounds_results_dfs = []
    for results_df in results_dfs:
        outrounds = ['Final' in round_name or 'pen' in round_name
                     for round_name in results_df['Round Name']]
        outrounds_results_df = results_df[pd.Series(outrounds)]
        outrounds_results_dfs.append(outrounds_results_df)
    return outrounds_results_dfs


if __name__ == '__main__':
    results_dfs = get_results_dfs('scraped_data/')
    print(team_positions_stats(results_dfs))
    #
    # outrounds_results_dfs = get_finals_rankings_dfs(results_dfs)
    # print(team_positions_stats(outrounds_results_dfs))

    # import scrape_results
    # from selenium import webdriver
    # from selenium.webdriver.chrome.service import Service
    # s = Service('C:\\Users\\Dell\\.wdm\\drivers\\edgedriver\\win64\\98.0.1108.62\\msedgedriver.exe')
    # driver = webdriver.Edge(service=s)
    #
    # dfs = scrape_results.scrape_all_results(
    #     'https://oxford2021.calicotab.com/oxfordiv2021/motions/statistics/', driver)
    # for round in round_by_round_stats(dfs):
    #     print(round)
    #
    # driver.close()
