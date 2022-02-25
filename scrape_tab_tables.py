"""A webscraping and data collection program for Debate tabs."""

from bs4 import BeautifulSoup
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from typing import List, Dict


# url_extensions = {' - Speakers': 'tab/speaker/', ' - Novices': 'tab/speaker/novice/',
#                   ' - Teams': 'tab/team/'}
url_extensions = {' - Speakers': 'tab/speaker/', ' - Teams': 'tab/team/'}


def save_tabs_from_file(filepath: str) -> None:
    """Store all tabs into CSV files."""
    # todo: take tournament name and tab URL and output a series of CSV files
    s = Service(EdgeChromiumDriverManager().install())  # get the latest Edge driver for Selenium
    driver = webdriver.Edge(service=s)  # prepare the browser window

    f = open(filepath, "r")  # open the file
    for row in f:  # for each tournament in the file
        cols = [col.strip() for col in row.split(',')]  # separate tournament name from URL
        if cols[1][-1] != '/':  # append a / at the end of the URL if not already there
            cols[1] += '/'
        for tab in url_extensions.keys():  # scrape for each page in the url_extensions dictionary
            df = scrape_tab_table(cols[1] + url_extensions[tab], driver)  # scrape table
            df = clean_tab_table(df)  # clean the data a bit
            df.to_csv(cols[0] + tab + '.csv')  # save as CSV
    driver.close()


def scrape_tab_table(url: str, driver: webdriver.Edge) -> pd.DataFrame:
    """Return a dataframe the containing data in a given speaker score table.
    The data is not cleaned up or abridged in any way."""
    # find the table element containing our tab data
    driver.get(url)  # open webpage
    content = driver.page_source  # get HTML
    soup = BeautifulSoup(content, features="html.parser")  # feed bs4 the HTML
    table = soup.find('table', attrs={'class': 'table'})

    # make a list of column headers in the table
    table_head = table.find('thead').find('tr').findAll('th')
    headers = []
    for ele in table_head:
        if ele.has_attr('data-original-title'):
            headers.append(ele['data-original-title'])
        else:
            headers.append(ele.findAll('span')[0].text.strip())
    # for ele in table_head:
    #     if ele.text == '':
    #         # if there isn't a name given, take the class name and extract a descriptive substring
    #         headers.append(ele['class'][1][5:].strip())
    #     else:  # if there is a name given, add the raw text
    #         headers.append(ele.text.strip())

    # identify the row elements
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')

    data = []  # the list we will fill with the cleaned data
    for row in rows:  # clean every row and add to data
        elements = process_row(row, headers)
        data.append(elements)

    df = pd.DataFrame(data, columns=headers)  # make a df
    df.reset_index(drop=True)  # remove index column
    return df


def process_row(row, headers) -> list:
    """Cleans up each row in the tab before returning the row."""
    elements = []  # the goal is to clean up the row elements and put them in this list
    cols = row.find_all('td')  # access columns for the given row
    regex_checker = re.compile(r'R[1-9]+')  # regex checker to identify round names

    for ele_index in range(len(headers)):
        if headers[ele_index] == 'Team':  # handling team names
            # team names are most cleanly written in a nested span HTML element, which this accesses
            elements.append(cols[ele_index].findAll('span')[0].get_text(strip=True))
        # check if there is data when you hover e.g. the other teams in the round
        elif regex_checker.match(headers[ele_index]):
            popups = cols[ele_index].findAll('div', {'class': 'popover-body'})
            if len(popups) == 0:  # if there is no popup data
                elements.append(cols[ele_index].text.strip())  # just append raw text
            else:  # if there is popup data
                ranking = cols[ele_index].find('span', {'hidden': 'hidden'}).text.strip()
                popup_elements = [popup_ele.get_text(strip=True)  # get all popup data
                                  for popup_ele in popups[0].findAll('span')]

                # fix some team data
                popup_elements[0] = popup_elements[0].replace('Teams in debate:', '')
                # add the row data as {teams} {total speaker score} {ranking}
                elements.append(str.join(' ', popup_elements + [ranking]))
        else:
            elements.append(cols[ele_index].text.strip())  # just add raw text
    return elements


def clean_tab_table(df: pd.DataFrame) -> pd.DataFrame:
    """Make the speaker scores dataframe more understandable."""
    # clarify table headers
    df = df.rename(columns={'Rk': 'Rank', 'name': 'Debater', 'team': 'Team',
                            'category': 'Categories', 'categories': 'Categories'})

    # eliminate duplicate values in individual cells e.g. '1 1' becomes '1'
    for colname in {'Rank', 'Avg', 'Total', 'Stdev', 'Trim', 'Pts', 'Spks', '1sts', '2nds',
                    'Points', 'Total speaker score', 'Speaker score standard deviation',
                    'Number of firsts', 'Number of seconds'}:
        if colname in df.columns:
            df[colname] = [row.split(' ')[-1] for row in df[colname]]

    return df


if __name__ == "__main__":
    save_tabs_from_file('Speaker Tabs.txt')
