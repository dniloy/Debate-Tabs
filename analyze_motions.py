"""A script to create motions statistics CSV files for individual tournaments."""
import pandas as pd
import re
from typing import List


def generate_motion_statistics(tournament_name: str) -> None:
    """Takes teams tab and motions list CSV files and outputs a motions tab dataframe and
    stores it as a CSV file."""
    teams_df = pd.read_csv(tournament_name + " - Teams.csv")  # load team tab df
    motions_df = pd.read_csv(tournament_name + " - Motions.csv")  # load motions df

    rounds_scores = []  # to fill with the scores from the rounds
    for row in motions_df['Round']:  # for each round as shown in motions
        # calculate the position scores from each round and add them to rounds_scores
        round_scores = calculate_round_positions(teams_df, motions_df, row)
        rounds_scores.append(round_scores)
    motions_df['Position Scores'] = rounds_scores  # create a new df column for scores

    gov_scores, opp_scores, opening_scores, closing_scores = [], [], [], []
    for index, row in motions_df.iterrows():
        # form a list of integers of scores for each round
        scores = [int(score) for score in list(row['Position Scores'])]
        gov_scores.append(scores[0] + scores[2])  # add gov scores
        opp_scores.append(scores[1] + scores[3])  # add gov scores
        opening_scores.append(scores[0] + scores[1])  # add gov scores
        closing_scores.append(scores[2] + scores[3])  # add gov scores
    motions_df['Gov'] = gov_scores
    motions_df['Opp'] = opp_scores
    motions_df['Opening'] = opening_scores
    motions_df['Closing'] = closing_scores

    motions_df.to_csv(tournament_name + ' - Motions Tab.csv')


def calculate_round_positions(teams_df: pd.DataFrame, motions_df: pd.DataFrame, round: str) \
        -> List[int]:
    """Return a list containing the total scores that each position (e.g. OG) achieved in the given
    round."""
    scores = [0, 0, 0, 0]  # four indices for four positions

    # each row corresponds to a team
    for index, row in teams_df.iterrows():
        # if the team didn't partake in the round
        # TODO: what if the round name is not in the teams csv?
        if round not in row or row['Team'] not in row[round]:
            continue
        # calculating the team's score
        score = int(row[round][-1])
        # splitting the round data by team position e.g. by the string '(OG)'
        # remove last item, which is round results
        teams_in_debate = re.split(r'\([OC][GO]\)', row[round])[:-1]
        teams_in_debate = [team.strip() for team in teams_in_debate]

        # add the team's score to the list
        team_position = teams_in_debate.index(row['Team'])
        scores[team_position] = scores[team_position] + score

    return scores


def calculate_round_positions2(teams_df: pd.DataFrame, motions_df: pd.DataFrame, round: str)\
        -> List[int]:
    """Return a list containing the total scores that each position (e.g. OG) achieved in the given
    round."""
    scores = [0, 0, 0, 0]  # four indices for four positions

    # each row corresponds to a team
    for index, row in teams_df.iterrows():
        # if the team didn't partake in the round
        # TODO: what if the round name is not in the teams csv?
        if round not in row or row['Team'] not in row[round]:
            continue
        # calculating the team's score
        score = int(row[round][-1])
        # splitting the round data by team position e.g. by the string '(OG)'
        # remove last item, which is round results
        teams_in_debate = re.split(r'\([OC][GO]\)', row[round])[:-1]
        teams_in_debate = [team.strip() for team in teams_in_debate]

        # add the team's score to the list
        team_position = teams_in_debate.index(row['Team'])
        scores[team_position] = scores[team_position] + score

    return scores


if __name__ == '__main__':
    generate_motion_statistics('HHIV 2020')
