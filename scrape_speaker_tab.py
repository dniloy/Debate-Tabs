"""A script to scrape results tabs for speakers data."""

from bs4 import BeautifulSoup
import pandas as pd
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from pathlib import Path
from urllib.parse import urljoin

from typing import List, Dict, Tuple


BASE_DIR = "D:\\GitHub\\Debate-Tabs"


def save_speaker_tab(tournament_name: str, speaks_url: str, driver: webdriver.Edge) -> None:
    filepath = Path('scraped_data/' + tournament_name + ' - Speakers.csv')
    filepath.parent.mkdir(parents=True, exist_ok=True)
    if os.path.exists(filepath):
        return

    df = scrape_speaker_tab(speaks_url, driver)  # get database containing speaker tabs
    if df.empty:
        return

    df.to_csv(filepath)  # save as csv


def scrape_speaker_tab(url: str, driver: webdriver.Edge) -> pd.DataFrame:
    """Returns a dataframe containing adjudicators and team rankings for the given round URL."""
    valid_url = get_speaker_tab_url(url, driver)
    if valid_url == '':
        return pd.DataFrame()

    driver.get(valid_url)  # load results url
    soup = BeautifulSoup(driver.page_source, features="html.parser")

    # find table
    tables = soup.findAll('div', {'class': 'table-responsive-md'})  # find table
    if len(tables) == 0:  # if there is no div tag with the table, find a table tag
        tables = soup.findAll('table', {'class': 'table-responsive-md'})
    table = tables[0]
    table_headers = get_table_headers(table)  # find table headers

    names, teams, categories, rounds_speaks = [], [], [], []
    for row in table.find('tbody').findAll('tr'):  # for each row in the tab table
        # enter row into rounds_dict
        name, team, category, round_speak = process_row(row, table_headers)
        names.append(name)
        teams.append(team)
        categories.append(category)
        rounds_speaks.append(round_speak)

    df = pd.DataFrame()
    df['Name'] = names
    df['Team'] = teams
    df['Categories'] = categories
    df['Speaker Scores'] = rounds_speaks

    return df


def get_speaker_tab_url(speaks_url: str, driver: webdriver.Edge) -> str:
    """Returns a valid speaker tab if the given URl leads to one, and returns '' otherwise."""
    driver.get(speaks_url)  # doing this means that we no longer need to use the URL in the caller
    soup = BeautifulSoup(driver.page_source, features="html.parser")

    for a in soup.findAll('a', {'class': 'nav-link'}):
        if 'Speaker Tab' in a:
            return urljoin(speaks_url, a['href'])
    return ''


def get_table_headers(table: BeautifulSoup) -> List[str]:
    """Returns the headers of the given table as a list of strings."""
    table_header_elements = table.find('thead').find('tr').findAll('th')  # find header elements
    table_headers = []  # fill with headers
    for element in table_header_elements:  # for each header element
        if element.has_attr('data-original-title'):  # if this attribute is present, life is easy
            table_headers.append(element.get('data-original-title'))
        else:  # otherwise, a span tag should contain the header
            table_headers.append(element.find('span').text.strip())
    return table_headers


def process_row(row: BeautifulSoup, headers: list) -> tuple:
    cols = row.findAll('td')
    name, team, categories = '', '', ''

    name = cols[headers.index('Name')].find('span').text.strip()
    if 'Team' in headers:
        team = cols[headers.index('Team')].find('span').text.strip()
    if 'Categories' in headers:
        categories = cols[headers.index('Categories')].find('span').text.strip()

    rounds_speak = []
    re_round = re.compile(r'R[0-9]+')
    for i in range(len(headers)):
        if re_round.match(headers[i]):
            # headers[i] = headers[i].replace('R', 'Round ')
            rounds_speak.append(cols[i].find('span').text.strip())

    return name, team, categories, rounds_speak


if __name__ == '__main__':
    s = Service(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=s)
    save_speaker_tab("Western IV 2021", 'https://westerniv.herokuapp.com/western2021/tab/speaker/',
                     driver)
    save_speaker_tab("HHIV 2020", 'https://naudc2021.calicotab.com/_/tab/speaker/', driver)
    driver.close()
