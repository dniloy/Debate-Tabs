"""Analyzes results files for data."""
import pandas as pd
import os
import re
from pathlib import Path


def get_team_positions_list() -> None:
    two_teams_positions_list = [0, 0]  # list for two-team formats e.g. Australs
    four_teams_positions_list = [0, 0, 0, 0]  # list for four-team formats e.g. BP
    set_of_team_positions = set()  # to find the unique list of team positions

    # get filepath for scraped data directory
    filepath = Path('scraped_data/')
    filepath.parent.mkdir(parents=True, exist_ok=True)
    for file in os.listdir(filepath):  # iterate through all the scraped data
        if file[-14:] == ' - Results.csv':  # if results file
            # find the file's filepath and get the dataframe
            filepath = Path('scraped_data/' + file)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            results_df = pd.read_csv(filepath)

            for room in results_df['Rankings']:  # for every room in the file
                teams = room.split('\', \'')  # split teams by commas
                teams[0] = teams[0][2:]  # remove the [' at the start
                teams[-1] = teams[-1][:-2]  # remove the '] at the end
                for team in teams:  # for each team in the room
                    position = re.search(r'\([A-Z]+\)', team[-4:])  # find team position substring
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
    # print stats
    print(normalized_two)
    print(normalized_four)
    print(normalized_bp_two)


def count_debates(folder: str) -> int:
    """Count total number of debates in the given folder.

    Preconditions
        - folder starts without '/' and ends with '/'"""
    # find folder containing debates data
    filepath = Path(folder)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    debate_count = 0

    for file in os.listdir(filepath):  # for every file in the given folder
        if file[-14:] == ' - Results.csv':  # if results file
            # get file's filepath
            filepath = Path(folder + file)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            df = pd.read_csv(filepath)  # convert file to dataframe
            debate_count += len(df['Rankings'])  # add number of rooms to debate_count
    return debate_count


if __name__ == '__main__':
    print(count_debates('scraped_data/'))
