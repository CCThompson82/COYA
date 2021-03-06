"""
Module of utility functions used in merging, filtering, updating, etc data structures in this
project.
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from copy import deepcopy
from fuzzywuzzy import process
from datetime import datetime
from dateutil import parser, relativedelta


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
    DIGITS = 3
    names = name.split(' ')
    if len(names) == 2:
        last = format_name(names[1])
        first = format_name(names[0])
        name_index = '_'.join([last, first[:DIGITS]])
    else:
        last = format_name(names[-1])
        first = format_names(names[:-1])
        name_index = '_'.join([last, first[:DIGITS]])
    return last, first, name_index


def format_name(name):
    """"""
    return name.lower().title()


def format_names(names):
    names = [format_name(name) for name in names]
    return ' '.join(names)


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


def find_outstanding(internal, external):
    """

    Args:
        internal:
        external:

    Returns:

    """
    THRESHOLD = 90
    best_matches = [process.extractOne(query, internal.index_name) for query in external.index_name]
    registered = [best_match for best_match in best_matches if best_match[1] > THRESHOLD]
    filter_index = np.isin(internal.index_name, [filter_name[0] for filter_name in registered])

    return ~filter_index


def format_player_registrations(raw_dataframe, feature_map):
    """

    Args:
        raw_dataframe:

    Returns:

    """
    dataframe = format_feature_names(raw_dataframe=raw_dataframe, feature_map=feature_map)
    dataframe = reformat_names(dataframe=dataframe)
    dataframe = format_dob(dataframe=dataframe)
    dataframe = format_postcode(dataframe=dataframe)
    dataframe = format_address(dataframe=dataframe)

    return dataframe


def reformat_names(dataframe):
    for column in ['first', 'last']:
        dataframe[column] = [format_name(name) for name in dataframe[column]]
    return dataframe


def format_address(dataframe):
    dataframe['address'] = dataframe['address'].astype(str).apply(str.title)
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


def filter_by_timestamp(df, key, months):
    """Filter a Timestamp series to entries within the last given months arg"""
    threshold = datetime.now() - relativedelta.relativedelta(months=months)
    series = deepcopy(df[key]).apply(parser.parse)
    return df.loc[series > threshold]
