"""Scrapes motions tabs. Not Motion statistics tabs."""

from bs4 import BeautifulSoup
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from typing import List, Dict, Tuple


def scrape_motions(tournament_name: str, url: str, driver: webdriver.Edge)\
        -> None:
    """Given a filepath containing tournament name and basic URL, extracts data each round on
    motion and infoslide."""
    driver.get(url)  # load website
    soup = BeautifulSoup(driver.page_source, features="html.parser")  # feed HTML into bs4

    round_names, info_slides, motions = choose_scraper(soup, tournament_name, url)

    # create a dataframe out of this data
    df = pd.DataFrame()
    df['Round'] = round_names
    df['Info Slide'] = info_slides
    df['Motion'] = motions
    df.reset_index(drop=True, inplace=True)

    df.to_csv(tournament_name + ' - Motions.csv')  # save dataframe to CSV


def choose_scraper(soup: BeautifulSoup, tournament_name: str, url: str) -> Tuple[List, List, List]:
    """Choose the scraper to use based on the website then return the columns"""
    if 'calico' in url:  # if calico tab website
        if 'statistics' in url:
            rounds_tag = ('div', {'class': 'list-group mt-3'})
            round_name_tag = ('span', {'class': 'badge badge-secondary'})
            motion_text_tag = ('h4', {'class': 'mb-3 mt-1'})
        else:
            rounds_tag = ('div', {'class': 'list-group list-group-flush'})
            round_name_tag = ('h4', {'class': 'card-title mt-0 mb-2 d-inline-block'})
            motion_text_tag = ('div', {'class': 'mr-auto pr-3 lead'})
    else:  # if herokuapp website
        if 'statistics' in url:
            rounds_tag = ('div', {'class': 'list-group mt-3'})
            round_name_tag = ('span', {'class': 'badge badge-secondary'})
            motion_text_tag = ('h4', {'class': 'mb-4 mt-2'})
        else:
            rounds_tag = ('div', {'class': 'card mt-3'})
            round_name_tag = ('h4', {'class': 'card-title mt-0 mb-2 d-inline-block'})
            motion_text_tag = ('div', {'class': 'mr-auto pr-3 lead'})
    return scrape(soup, rounds_tag, round_name_tag, motion_text_tag)


def scrape(soup: BeautifulSoup, rounds_tag: tuple, round_name_tag: Tuple[str, dict],
           motion_text_tag: Tuple[str, dict]):
    rounds = soup.findAll(*rounds_tag)
    round_names, info_slides, motions = [], [], []
    for round in rounds:  # search list of rounds
        # get round name
        round_name = round.findAll(*round_name_tag)[0].text.strip()
        round_names.append(round_name)

        # search for the motion text
        motions.append(round.findAll(*motion_text_tag)[0].text.strip())

        # search for anything that could be an infoslide
        infoslide_elements = round.findAll('div', {'class': 'modal-body lead'})
        if len(infoslide_elements) > 0:  # if there is an infoslide, add it
            # collect the paragraphs in the infoslide
            infoslide_text = str.join('\n', [paragraph.text.strip()
                                             for paragraph in
                                             infoslide_elements[0].findAll('p')])
            info_slides.append(infoslide_text)
        else:  # if there are no infoslides, add an empty string
            info_slides.append('')
    return round_names, info_slides, motions


if __name__ == '__main__':
    s = Service(EdgeChromiumDriverManager().install())  # get the latest Edge driver for Selenium
    driver = webdriver.Edge(service=s)  # prepare the browser window
    scrape_motions("NAUDC 2020", 'https://naudc2021.calicotab.com/_/motions/statistics/', driver)
    scrape_motions("HHIV 2020",
                   'https://hhiv2020.calicotab.com/hhiv2020/motions/statistics/', driver)
    scrape_motions("HHIV 2019",
                   "https://hhiv2020.calicotab.com/hhiv2020/motions/", driver)
    scrape_motions("Chancellor's 2019",
                   'https://chancellors2019.herokuapp.com/chancellors2019/motions/', driver)
    driver.close()
