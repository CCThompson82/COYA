"""
Module of utility functions used in merging, filtering, updating, etc data structures in this
project.
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from copy import deepcopy
from datetime import datetime

def names_to_dataframe(names):
    """
    Converts a list of str "first last" names into a formatted tuple useful in downstream
        merge/search steps

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


def dataframe_to_list(dataframe, feature_name_map):
    """
    Converts a partially formatted player dataframe into a list of str ("first last")

    Args:
        dataframe (pd.DataFrame):
        feature_name_map (dictionary) maps the known feature names to first, last, etc.
            e.g. {'first': "First name": , 'last': "Surname": }

    Returns:
        names_ls
    """
    filtered_df = dataframe.loc[:, [feature_name_map['first'], feature_name_map['last']]]
    names_ls = filtered_df.values.tolist()

    for idx, name in enumerate(names_ls):
        names_ls[idx] = " ".join([_name.strip() for _name in name]).title()
    return names_ls


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


def find_outstanding(internal, external, keep_outstanding=True):
    """

    Args:
        internal:
        external:
        keep_outstanding:

    Returns:

    """
    filter_index = np.isin(internal.index_name,
                           external.index_name)
    if keep_outstanding:
        return ~filter_index
    return filter_index


def format_player_registrations(raw_dataframe, feature_map):
    """

    Args:
        raw_dataframe:

    Returns:

    """
    dataframe = format_feature_names(raw_dataframe=raw_dataframe, feature_map=feature_map)
    dataframe = format_dob(dataframe=dataframe)
    dataframe = format_postcode(dataframe=dataframe)
    dataframe = format_address(dataframe=dataframe)

    return dataframe


def format_address(dataframe):
    dataframe['address'] = dataframe['address'].apply(str.title)
    return dataframe


def format_postcode(dataframe):
    postcodes = dataframe['postcode']

    for idx, postcode in enumerate(postcodes):
        postcode = postcode.strip()
        region, inward = postcode[:-3].upper().strip(), postcode[-3:].upper().strip()
        dataframe.ix[idx, 'postcode'] = ' '.join([region, inward])

    return dataframe


def format_dob(dataframe):
    dataframe['dob'] = pd.to_datetime(dataframe['dob'], infer_datetime_format=True)
    dataframe['dob'] = pd.Series(
        [entry.strftime('%Y-%m-%d') for entry in dataframe['dob']])
    return dataframe


def format_feature_names(raw_dataframe, feature_map):
    keys = ['first', 'last', 'dob', 'postcode', 'address']
    columns = [feature_map[key] for key in keys]
    dataframe = deepcopy(raw_dataframe)
    dataframe = dataframe.loc[:, columns]
    dataframe.columns = keys
    dataframe.columns = ['first', 'last', 'dob', 'postcode', 'address']
    return dataframe
