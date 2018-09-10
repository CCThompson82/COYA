"""
client module for reading, writing to the actonians google sheet database.

NOTES
* credentials are untracked for security purposes
* all sheets to be accessed with this client are required to be shared with the email address
listed as the `client_email` in the service account credentials json file.
"""
import os
import gspread
import numpy as np
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

WORKDIR = '/work'
CREDENTIAL_PATH = os.path.join(WORKDIR, 'credentials', 'actoniansDB-c026e3ac44e8.json')
SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CREDENTIALS = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIAL_PATH, SCOPES)
CLIENT = gspread.authorize(CREDENTIALS)
RESPONSES_BASE = 'Actonians AFC Registration {} (Responses)'
REGISTER_BASE = 'Outstanding SAL Registrations ({})'


def get_responses(year='2018-2019'):
    """
    Retrieves raw member registration googlesheet

    Args
        year (str): season spanning, e.g. 2018-2019

    Returns
        responses (pd.DataFrame)
    """
    files_ls = CLIENT.list_spreadsheet_files()
    filter_bool = [record['name'] == RESPONSES_BASE.format(year) for record in files_ls]
    key = np.array(files_ls)[filter_bool][0]['id']

    records_ls = CLIENT.open_by_key(key).get_worksheet(index=0).get_all_values()

    responses = pd.DataFrame(records_ls[1:], columns=records_ls[0])
    return responses


def put_registrations(outstanding, year='2018-2019'):
    """
    Opens the

    Args:
        year:

    Returns:

    """
    files_ls = CLIENT.list_spreadsheet_files()
    filter_bool = [record['name'] == REGISTER_BASE.format(year) for record in files_ls]
    key = np.array(files_ls)[filter_bool][0]['id']

    registry_con = CLIENT.open_by_key(key)
    registry_con.del_worksheet(registry_con.worksheet('league_outstanding'))
    registry_con.add_worksheet('league_outstanding', *outstanding.shape)
    outstanding_con = registry_con.worksheet('league_outstanding')

    cells = []
    for col_idx, col in enumerate(outstanding.columns):
        cells.append(gspread.Cell(1, col_idx + 1, col))
    for row_idx in range(len(outstanding)):
        for col_idx, value in enumerate(outstanding.iloc[row_idx]):
            cells.append(gspread.Cell(row_idx + 2, col_idx + 1, value))

    outstanding_con.update_cells(cells)











