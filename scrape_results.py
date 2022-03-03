"""A script to scrape results tabs for team data."""

from bs4 import BeautifulSoup
import pandas as pd
import re
import os.path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from urllib.parse import urljoin
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from pathlib import Path
from typing import List, Dict


def save_all_results(tournament_name: str, base_url: str, driver: webdriver.Edge) -> None:
    filepath = Path('scraped_data/' + tournament_name + ' - Results.csv')
    filepath.parent.mkdir(parents=True, exist_ok=True)
    if os.path.exists(filepath):
        return

    df = scrape_all_results(base_url, driver)
    if df.empty:
        return

    df.to_csv(filepath)  # save as csv


def scrape_all_results(tournament_url: str, driver: webdriver.Edge) -> pd.DataFrame:
    """Return a single dataframe containing scraped results data from all rounds at the given
    tournament URL.

    Preconditions:
        - url is a tabbycat link"""
    driver.get(tournament_url)
    soup = BeautifulSoup(driver.page_source, features="html.parser")

    # Find all results links. Note: if there are none, an empty dataframe is returned.
    round_menu = soup.findAll('div', {'class': 'dropdown-menu', 'aria-labelledby': 'roundsDrop'})
    if len(round_menu) == 0:
        return pd.DataFrame()
    else:
        rounds = round_menu[0].findAll('a', {'class': 'dropdown-item'})

    # fill list with the scraped data from each round
    rounds_dfs = []
    for round in rounds:
        result_url = urljoin(tournament_url, round['href'])  # get the full url for the results page
        rounds_dfs.append(scrape_results(result_url, driver))  # append scraped results data

    # concatenate the results into one dataframe
    df = pd.DataFrame()
    for round_df in rounds_dfs:
        df = pd.DataFrame.append(self=df, other=round_df, ignore_index=True)

    return df


def scrape_results(results_url: str, driver: webdriver.Edge) -> pd.DataFrame:
    """Returns a dataframe containing adjudicators and team rankings for the given round URL."""
    driver.get(results_url)
    soup = BeautifulSoup(driver.page_source, features="html.parser")  # feed HTML into bs4

    tables = soup.findAll('div', {'class': 'table-responsive-md'})  # find table
    if len(tables) == 0:
        tables = soup.findAll('table', {'class': 'table-responsive-md'})
    table = tables[0]
    table_headers = get_table_headers(table)  # find table headers

    rooms_dict = {}  # this will be filled with the data from every room in the round
    for row in table.find('tbody').findAll('tr'):  # for each row in the tab table
        # enter row into rounds_dict
        process_row(rooms_dict, row, results_url, table_headers)

    rooms_panel, rooms_rankings = [], []
    for adj in rooms_dict:
        rooms_panel.append(adj)
        # room[0] is the ranking score, sort in descending order of ranking
        room_rankings = sorted(rooms_dict[adj], key=lambda room: int(room[0]), reverse=True)
        rooms_rankings.append(room_rankings)

    df = pd.DataFrame()
    df['Round Name'] = [soup.find('small').text.strip()[4:]] * len(rooms_panel)
    df['Panel'] = rooms_panel
    df['Rankings'] = rooms_rankings

    return df


def get_table_headers(table: BeautifulSoup) -> List[str]:
    """Returns the headers of the given table as a list of strings."""
    table_header_elements = table.find('thead').find('tr').findAll('th')  # find header elements
    table_headers = []  # fill with headers
    for element in table_header_elements:  # for each header element
        if element.has_attr('data-original-title'):  # if this attribute is present, life is easy
            table_headers.append(element.get('data-original-title'))
        elif len(element.findAll('span')) != 0:
            table_headers.append(element.find('span').text.strip())
    # if there's something with no text at all, I think I can just skip it and let it not be
    # added to the dataframe
    return table_headers


def process_row(rooms_dict: dict, row: BeautifulSoup, url: str, headers: list) -> None:
    """Mutates rounds_dict to add the panel as a key and list of teams (ordered by ranking) as
    value."""
    round_adj_elements = row.findAll('td', {'class': 'adjudicator-name'})  # find adjudicator td
    if len(round_adj_elements) == 0:  # if no td element of class 'adjudicator-name' name found
        round_adj_elements = [element for element in row.findAll('td')  # collect row elements
                              if 'adj' in str(element)]  # if 'adj' anywhere in element
        if len(round_adj_elements) == 0:  # if still no adj name found, don't modify rounds_dict
            return
    # get adj name from the correct span element
    round_adj_name = round_adj_elements[0].find('span', {'class': 'tooltip-trigger'}).text.strip()
    if round_adj_name not in rooms_dict:  # if the current room isn't already in rooms_dict
        rooms_dict[round_adj_name] = []

    # todo: outrounds don't have all four rankings
    # todo: finals rounds go 2-1-1-1
    cols = row.findAll('td')  # get row elements
    team_name = cols[headers.index('Team')].find('span').text.strip()  # scrape team name
    # scrape the words in team position e.g. ['Opening', 'Opposition'] or ['Government']
    team_position_list = cols[headers.index('Side')].find('span').text.split()
    team_position = team_position_list[0][0]  # abbreviate position
    if len(team_position_list) > 1:
        team_position += team_position_list[1][0]

    # scrape number of points earned by the team e.g. 3 for 1st
    ranking = int(cols[headers.index('Result')].find('span').text.strip()) - 1
    rooms_dict[round_adj_name].append(str(ranking) + ' ' + team_name + ' (' + team_position + ')')


def find_tabs_without_results_from_csv(filepath: str, driver: webdriver.Edge) -> list:
    """Returns a list of URLs that have no results."""
    urls = []
    df = pd.read_csv(filepath)
    for url_float in set(df['Event_Link']):  # iterate through event links
        for url in str(url_float).split():  # sometimes there are multiple links, so analyze each
            # todo: deal with (lse2021.herokuapp.com)
            if 'calico' in url or 'heroku' in url:  # if tabbycat link
                print(url)
                driver.get(url)
                if 'results/round/1' not in driver.page_source:
                    print('no results')
                    urls.append(url)
    return urls


def test_scrape_results() -> None:
    s = Service('C:\\Users\\Dell\\.wdm\\drivers\\edgedriver\\win64\\98.0.1108.62\\msedgedriver.exe')
    driver = webdriver.Edge(service=s)
    # print(scrape_all_results('https://westerniv.herokuapp.com/', driver))
    # print(scrape_all_results('https://hhiv2020.calicotab.com/hhiv2020/', driver))
    # print(scrape_all_results('https://cinnamonscroll.herokuapp.com/cinnamonscroll2020/', driver))
    print(scrape_all_results('http://easters2016.herokuapp.com/auea16/', driver))

    driver.close()


if __name__ == '__main__':
    # test_scrape_results()
    s = Service('C:\\Users\\Dell\\.wdm\\drivers\\edgedriver\\win64\\98.0.1108.62\\msedgedriver.exe')
    driver = webdriver.Edge(service=s)
    save_all_results('2021-07-07 WUDC 2021', 'https://wudckorea.calicotab.com/2021/', driver)
    driver.close()
    # find_tabs_without_results_from_csv("Debating_Motions - Motions (Grey-_Added).csv", driver)
