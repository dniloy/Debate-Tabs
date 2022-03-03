"""Scrapes motions tabs. Not Motion statistics tabs."""

import pandas as pd
import os.path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from typing import List, Dict, Tuple
from pathlib import Path
from urllib.parse import urljoin


def save_all_motions(tournament_name: str, base_url: str, driver: webdriver.Edge) -> None:
    """Saves in a csv file all motions from the given tournament"""
    filepath = Path('scraped_data/' + tournament_name + ' - Motions.csv')
    filepath.parent.mkdir(parents=True, exist_ok=True)
    if os.path.exists(filepath):
        return

    df = scrape_motions(base_url, driver)
    if df.empty:
        return

    df.to_csv(filepath)  # save as csv


def scrape_motions(base_url: str, driver: webdriver.Edge) -> pd.DataFrame:
    """Given a filepath containing tournament name and basic URL, extracts each round's name,
    motion and infoslide."""
    valid_url = get_valid_motions_url(base_url, driver)
    if valid_url == '':
        return pd.DataFrame()

    driver.get(valid_url)  # load website
    soup = BeautifulSoup(driver.page_source, features="html.parser")  # feed HTML into bs4

    round_names, info_slides, motions = choose_scraper(soup, valid_url)

    # create a dataframe out of this data
    df = pd.DataFrame()
    df['Round'] = round_names
    df['Info Slide'] = info_slides
    df['Motion'] = motions

    return df


def get_valid_motions_url(base_url: str, driver: webdriver.Edge) -> str:
    """Returns a valid speaker tab if the given URl leads to one, and returns '' otherwise."""
    driver.get(base_url)  # doing this means that we no longer need to use the URL in the caller
    soup = BeautifulSoup(driver.page_source, features="html.parser")

    for a in soup.findAll('a', {'class': 'nav-link'}):
        if 'motions' in a['href']:
            return urljoin(base_url, a['href'])
    return ''


def choose_scraper(soup: BeautifulSoup, url: str) -> Tuple[List, List, List]:
    """Choose the scraper to use based on the website then return the columns"""
    # choose the scraper by setting the appropriate values of these three variables
    # based on the if-else cases
    rounds_tag, round_name_tag, motion_text_tag = ('', {}), ('', {}), ('', {})

    if 'calico' in url:  # if calico tab website
        if 'statistics' in url:  # if it's a motion statistics URL
            rounds_tag = ('div', {'class': 'list-group mt-3'})
            round_name_tag = ('span', {'class': 'badge badge-secondary'})
            motion_text_tag = ('h4', {'class': 'mb-3 mt-1'})
            # motion_text_tag = ('h4',)
        elif 'motion' in url:  # if it's a motions tab URL
            rounds_tag = ('div', {'class': 'list-group list-group-flush'})
            round_name_tag = ('h4', {'class': 'card-title mt-0 mb-2 d-inline-block'})
            motion_text_tag = ('div', {'class': 'mr-auto pr-3 lead'})

        return scrape_rounds(soup, rounds_tag, round_name_tag, motion_text_tag)
    elif 'heroku' in url:  # if herokuapp website
        if 'statistics' in url:  # if it's a motion statistics URL
            rounds_tag = ('div', {'class': 'list-group mt-3'})
            round_name_tag = ('span', {'class': 'badge badge-secondary'})
            motion_text_tag = ('h4', {'class': 'mb-4 mt-2'})
            # motion_text_tag = ('h4',)
        elif 'motion' in url:  # if it's a motions tab URL
            rounds_tag = ('div', {'class': 'card mt-3'})
            round_name_tag = ('h4', {'class': 'card-title mt-0 mb-2 d-inline-block'})
            motion_text_tag = ('div', {'class': 'mr-auto pr-3 lead'})

        return scrape_rounds(soup, rounds_tag, round_name_tag, motion_text_tag)

    return [], [], []  # if the URL is invalid


def scrape_rounds(soup: BeautifulSoup, rounds_tag: tuple, round_name_tag: Tuple[str, dict],
                  motion_text_tag: Tuple[str, dict]):
    """For the given motions page, return the round names, infoslides and motions as three lists."""
    rounds = soup.findAll(*rounds_tag)
    # if there are no motions data, then I think empty data is returned?
    round_names, info_slides, motions = [], [], []
    for round in rounds:  # search list of rounds
        # get round name
        round_name = round.findAll(*round_name_tag)[0].text.strip()
        round_names.append(round_name)

        # search for the motion text
        print(rounds_tag, round_name_tag, motion_text_tag)
        motion_elements = round.findAll(*motion_text_tag)
        if len(motion_elements) == 0:
            motions.append('')
        else:
            motions.append(motion_elements[0].text.strip())

        # search for anything that could be an infoslide
        infoslide_elements = round.findAll('div', {'class': 'modal-body'})
        if len(infoslide_elements) > 0:  # if there is an infoslide, add it
            # collect the paragraphs in the infoslide
            infoslide_text = str.join('\n', [paragraph.text.strip()
                                             for paragraph in
                                             infoslide_elements[0].findAll('p')])
            info_slides.append(infoslide_text)
        else:  # if there are no infoslides, add an empty string
            info_slides.append('')
    return round_names, info_slides, motions


def test_scrapers() -> None:
    """Test each scraper."""
    s = Service('C:\\Users\\Dell\\.wdm\\drivers\\edgedriver\\win64\\98.0.1108.62\\msedgedriver.exe')
    driver = webdriver.Edge(service=s)

    # websites corresponding to each scraper.
    # print(scrape_motions("https://hhiv2020.calicotab.com/hhiv2020/", driver))
    # print(scrape_motions('https://naudc2021.calicotab.com/', driver))
    # print(scrape_motions('https://chancellors2019.herokuapp.com/', driver))
    # print(scrape_motions('https://yaleiv2018.herokuapp.com/', driver))
    print(scrape_motions('https://salty-wildwood-56548.herokuapp.com/Anudc19/motions/', driver))

    driver.close()


if __name__ == '__main__':
    test_scrapers()
    print("motion scraper script run")
