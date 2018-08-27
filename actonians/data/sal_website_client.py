"""
Client API for extracting information from the SAL website
"""

import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd

MATCH_PAGE_FOR_EXTRACTION = 'http://fulltime-league.thefa.com/DisplayFixture.do?id=18339889'


# TODO: Currently pulls all players for the Stewart Hyde Trophy match, which includes Poly players


def get_registered_players():
    """
    Returns:
        pd.DataFrame of registered players
    """
    soup = make_soup(url=MATCH_PAGE_FOR_EXTRACTION)

    names_ls = scrape_player_names(soup=soup)

    registered_players = names_to_registered_dataframe(names=names_ls)

    return registered_players


def names_to_registered_dataframe(names):
    """

    Args:
        names [first last]:

    Returns:
        all_reg_players (pd.DataFrame)
    """
    all_reg_players = pd.DataFrame(
        [], columns=['last', 'first', 'index_name'], index=range(len(names)))

    for idx_nb, name in enumerate(names):
        [last, first, index_name] = parse_name(name=name)
        all_reg_players.loc[idx_nb, :] = parse_name(name=name)

    return all_reg_players


def parse_name(name):
    names = name.split(' ')
    if len(names) == 2:
        last = names[1].title()
        first = names[0].title()
        name_index = '_'.join([names[1].title(), names[0][:3].title()])
    else:
        last = names[-1].title()
        first_ls = names[:-1]
        first_ls[0] = first_ls[0].title()
        first = ' '.join(first_ls)
        name_index = '_'.join([last, first[:3]])
    return last, first, name_index





def make_soup(url):
    """
    Args:
        url:

    Returns:
        BeautifulSoup object
    """
    html = urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def scrape_player_names(soup):
    """

    Args:
        soup (BeautifulSoup object):

    Returns:
        [players]
    """
    pattern = re.compile('DisplayStatsForPlayer')
    names_ls = []
    for tag in soup.find_all('a'):
        if not 'href' in tag.attrs.keys():
            continue

        href_str = tag.attrs['href']

        if pattern.search(href_str):
            names_ls.append(tag.text)
    return names_ls
