"""A webscraping and data collection program for Debate tabs."""

from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from typing import List


def scrape_speaker_scores(url: str) -> pd.DataFrame:
    """Return a dataframe the containing data in a given speaker score table.

    The data is not cleaned up or abridged in any way."""
    s = Service(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=s)
    driver.get(url)

    content = driver.page_source
    soup = BeautifulSoup(content, features="lxml")
    data = []
    table = soup.find('table', attrs={'class': 'table'})

    table_head = table.find('thead').find('tr').findAll('th')
    headers = []
    for ele in table_head:
        if ele.text == '':
            # if there isn't a name given, take the class name and extract a descriptive substring
            headers.append(ele['class'][1][5:])
        else:
            headers.append(ele.text)

    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append(cols)

    df = pd.DataFrame(data, columns=headers)
    return df


def clean_speaker_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Make the speaker scores dataframe more understandable."""
    df = df.rename(columns={'Rk': 'Rank', 'name': 'Debater', 'team': 'Team'})
    return df


if __name__ == "__main__":
    url = "https://hhhs2022.calicotab.com/hhhs2022/tab/speaker/"
    df = scrape_speaker_scores(url)
    clean_speaker_scores(df)
