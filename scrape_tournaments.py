import scrape_results
import scrape_motions
import scrape_speaker_tab
import pandas as pd
import validators
import os

from bs4 import BeautifulSoup
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import InvalidArgumentException, WebDriverException
from typing import List, Tuple
from pathlib import Path


def save_tournaments_from_file_tabbycat(filepath: str) -> None:
    df = pd.read_csv(filepath)

    tournaments_set = {(str(row['Date']) + ' ' + str(row['Tournament']), str(row['Event_Link']))
                       for index, row in df.iterrows()  # iterate rows
                       if str(row['Event_Link']) != 'nan'}  # if there is an event link

    # s = Service(EdgeChromiumDriverManager().install())  # install Edge drivers
    # driver = webdriver.Edge(service=s)  # start web driver service
    s = Service('C:\\Users\\Dell\\.wdm\\drivers\\edgedriver\\win64\\98.0.1108.62\\msedgedriver.exe')
    driver = webdriver.Edge(service=s)

    filepath = Path('scraped_data/Motions.csv')
    filepath.parent.mkdir(parents=True, exist_ok=True)
    for tournament in tournaments_set:
        print(tournament)
        # todo: deal with (lse2021.herokuapp.com)
        for url in tournament[1].split():  # sometimes there are multiple links, so analyze each
            if not validators.url(url):  # if url isn't a valid link
                continue
            elif 'calico' in url or 'heroku' in url:  # if url is a valid url and a tabbycat link
                try:  # append this tournament's motions to motions_df
                    scrape_motions.save_all_motions(tournament[0], url,
                                                    driver=driver)  # save motions
                    scrape_speaker_tab.save_speaker_tab(tournament[0], url,
                                                        driver=driver)  # save speaks
                    scrape_results.save_all_results(tournament[0], url,
                                                    driver=driver)  # save results
                # if error, just move to the next url
                # the urls that raise and error will be dealt with separately
                except (InvalidArgumentException, WebDriverException):
                    continue


def find_unscraped_tournaments(database: str, folder: str) -> set:
    df = pd.read_csv(database)
    filepath = Path(folder)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # generate a list of sets where each set contains the filenames expected to be generated for
    # each row
    set_of_expected_files = [{str(row['Date']) + ' ' + row['Tournament'] + ' - Results.csv',
                              str(row['Date']) + ' ' + row['Tournament'] + ' - Motions.csv',
                              str(row['Date']) + ' ' + row['Tournament'] + ' - Speakers.csv'}
                             for index, row in df.iterrows()  # for rows
                             # don't forget to split the event link string in case multiple urls
                             if validators.url(str(row['Event_Link'])) and  # if tabbycat link
                             ('calico' in row['Event_Link'] or 'heroku' in row['Event_Link'])]
    expected_files = set()
    for tournament in set_of_expected_files:
        expected_files = expected_files.union(tournament)

    # get filepath of folder containing scraped data
    filepath = Path(folder)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    print(len(expected_files))
    print(len(os.listdir(filepath)))

    return set.difference(expected_files, set(os.listdir(filepath)))


if __name__ == '__main__':
    print(find_unscraped_tournaments('Debating_Motions - Motions (Grey-_Added).csv',
                                     'scraped_data/'))
    save_tournaments_from_file_tabbycat('Debating_Motions - Motions (Grey-_Added).csv')
