"""
Call this script to generate a dataframe of players we need to register with the league, and
upload this list to our googlesheets account.
"""
import os
import sys
ROOT_DIR = os.environ['ROOT_DIR']
sys.path.append(ROOT_DIR)


import numpy as np
from actonians.data import gsheets_client as gs_client
from actonians.data import sal_website_client as sal_client
from actonians.data import db_utils

CAMPAIGN_YEAR = '2018-2019'
FEATURE_NAME_MAP = {'first': 'First name', 'last': 'Surname'}
LEAGUE_UPLOAD_MAP = {**FEATURE_NAME_MAP,
                     **{'dob': 'Date of Birth', 'postcode': 'Post Code',
                        'address': 'Street Address'}}


def find_outstanding_registrations():
    """

    Returns:

    """
    raw_internal_registrations = gs_client.get_responses(CAMPAIGN_YEAR)
    internal_names = db_utils.dataframe_to_list(
        dataframe=raw_internal_registrations,
        feature_name_map=FEATURE_NAME_MAP)
    internal_registrations = db_utils.names_to_dataframe(names=internal_names)
    external_registrations = sal_client.get_registered_players()

    outstanding_index = db_utils.find_outstanding(
        internal=internal_registrations, external=external_registrations)
    raw_outstanding = raw_internal_registrations.iloc[outstanding_index].reset_index()

    outstanding = db_utils.format_player_registrations(
        raw_dataframe=raw_outstanding, feature_map=LEAGUE_UPLOAD_MAP)

    return outstanding, internal_registrations


if __name__ == '__main__':

    outstanding_registrations, internal_registrations = find_outstanding_registrations()
    gs_client.put_outstanding_registrations(outstanding=outstanding_registrations)
    gs_client.put_internal_registrations(internal=internal_registrations)
