"""
Module of utility functions used in merging, filtering, updating, etc data structures in this
project.
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd


def names_to_dataframe(names):
    """

    Args:
        names [first last]:

    Returns:
        dataframe (pd.DataFrame)
    """
    dataframe = pd.DataFrame(
        [], columns=['last', 'first', 'index_name'], index=range(len(names)))

    for idx_nb, name in enumerate(names):
        dataframe.loc[idx_nb, :] = parse_name(name=name)

    return dataframe


def parse_name(name):
    """
    Converts a str "First Last" into separate fields, correcting for case mistakes and managing
    situations where more than 2 names have been given.

    Args:
        name:

    Returns:
        last, first, name_index
    """
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
