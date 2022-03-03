import scrape_results
import scrape_motions
import scrape_speaker_tab
import pandas as pd
import validators

from bs4 import BeautifulSoup
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from typing import List, Tuple
from pathlib import Path


def save_tournaments_from_file_tabbycat(filepath: str) -> None:
    df = pd.read_csv(filepath)

    tournaments_set = {(str(row['Date']) + ' ' + str(row['Tournament']), str(row['Event_Link']))
                       for index, row in df.iterrows()  # iterate rows
                       if str(row['Event_Link']) != 'nan'}  # if there is an event link
    tournaments = list(tournaments_set)  # convert set to tournaments list

    # s = Service(EdgeChromiumDriverManager().install())  # install Edge drivers
    # driver = webdriver.Edge(service=s)  # start web driver service
    s = Service('C:\\Users\\Dell\\.wdm\\drivers\\edgedriver\\win64\\98.0.1108.62\\msedgedriver.exe')
    driver = webdriver.Edge(service=s)

    filepath = Path('scraped_data/Motions.csv')
    filepath.parent.mkdir(parents=True, exist_ok=True)
    for tournament in tournaments:
        print(tournament)
        # todo: deal with (lse2021.herokuapp.com)
        for url in tournament[1].split():  # sometimes there are multiple links, so analyze each
            if not validators.url(url):
                continue
            elif 'calico' in url or 'heroku' in url:  # if it's a tabbycat link
                # append this tournament's motions to motions_df
                scrape_motions.save_all_motions(*tournament, driver=driver)  # save motions
                scrape_speaker_tab.save_speaker_tab(*tournament, driver=driver)  # save speaks
                scrape_results.save_all_results(*tournament, driver=driver)  # save results tabs


if __name__ == '__main__':
    save_tournaments_from_file_tabbycat('Debating_Motions - Motions (Grey-_Added).csv')
