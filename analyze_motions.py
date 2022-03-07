"""A script to create motions statistics CSV files for individual tournaments."""
import pandas as pd
import re
import os

from nltk.corpus import stopwords
from pathlib import Path
from typing import List, Tuple


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


def get_motions_dfs(folder: str) -> List[pd.DataFrame]:
    motions_dfs = []

    for file in os.listdir(folder):  # iterate through all the scraped data
        if file[-14:] == ' - Motions.csv':  # if results file
            # find the file's filepath and get the dataframe
            filepath = Path(folder + file)
            motions_df = pd.read_csv(filepath)
            motions_dfs.append(motions_df)

    return motions_dfs


def analyze_motions_frequency(motions_dfs: List[pd.DataFrame]) -> pd.DataFrame:
    info_slide_words = {}
    motion_words = {}
    for motions_df in motions_dfs:
        texts = motions_df['Info Slide'] + motions_df['Motion']
        for motion in texts:
            for word in str(motion).split():
                cleaned_word = re.sub(r'\W+', '', word).lower()
                if cleaned_word in stopwords.words('english'):
                    continue
                if cleaned_word in info_slide_words:
                    info_slide_words[cleaned_word] += 1
                else:
                    info_slide_words[cleaned_word] = 1

    df = pd.DataFrame(info_slide_words.items()).append(pd.DataFrame(motion_words.items()))
    df.columns = ['Word', 'Count']
    df = df.sort_values('Count', ascending=False)

    return df


if __name__ == '__main__':
    motions_dfs = get_motions_dfs('scraped_data/')
    df = analyze_motions_frequency(motions_dfs)
    print(df)
