"""
Client API for extracting information from the SAL website
"""

import re
from actonians.data import db_utils

MATCH_PAGE_FOR_EXTRACTION = 'http://fulltime-league.thefa.com/DisplayFixture.do?id=18878464'


# TODO: Currently pulls all players for the Stewart Hyde Trophy match, which includes Poly players
def get_registered_players():
    """
    Returns:
        pd.DataFrame of registered players
    """
    soup = db_utils.make_soup(url=MATCH_PAGE_FOR_EXTRACTION)
    names_ls = extract_player_names(soup=soup)
    registered_players = db_utils.names_to_dataframe(names=names_ls)

    return registered_players


# utils for sal scraping
def extract_player_names(soup):
    """

    Args:
        soup (BeautifulSoup object):

    Returns:
        [players]
    """
    pattern = re.compile('DisplayStatsForPlayer')
    names_ls = []
    for tag in soup.find_all('a'):
        if 'href' not in tag.attrs.keys():
            continue

        href_str = tag.attrs['href']

        if pattern.search(href_str):
            names_ls.append(tag.text)
    return names_ls
