"""Utils module

This script contains utility/helper functions for read/write related queries.

It contains following functions
    * find_in_json: Finds entry in JSON where key = value and returns it as dict
    * read_json: Reads JSON file and returns it as list[dict]
    * write_json: Writes list[dict] as json
    * write_csv: Writes pandas DataFrame as CSV file
"""

import json
import itertools
import pandas as pd

def find_in_json(json_data, key, value):
    """Finds entry in JSON where key = value and returns it as dict

    Parameters
    ----------
    key: str
        Attribute of the entry to be checked
    value: str
        Expected value of attribute
    
    Returns
    -------
    entry: dict
        Entry that fufills the condition
    """

    entry = None
    for j in json_data:
        if(j[key] == value):
            entry = j
            break
    return entry

def read_json(json_file):
    """Reads JSON file and returns it as list[dict]

    Parameters
    ----------
    json_file: str
        Location of JSON file to be read
    
    Returns
    -------
    data: list[dict]
        Data in JSON file as variable
    """

    data = None
    with open(json_file, 'r') as infile:
        data = json.load(infile)
    return data

def write_json(json_data, json_file):
    """Reads JSON file and returns it as list[dict]

    Parameters
    ----------
    json_data: list[dict]
        JSON data to be written in file
    json_file: str
        Location of JSON file to be written
    """

    with open(json_file, 'w') as outfile:
        json.dump(json_data, outfile, indent=4)

def write_csv(df, csv_loc):
    """Writes pandas DataFrame as CSV file

    Parameters
    ----------
    df: pd.DataFrame
        DataFrame to be written
    csv_loc: str
        Location of CSV file to be created
    """

    df.to_csv(csv_loc)

def get_close_df(csv_loc, file_name, start_date, end_date, series=True):
    col_list = ['Date', 'Close']
    temp_df = pd.read_csv("{}/{}".format(csv_loc,file_name), usecols=col_list)
    temp_df['Date'] = pd.to_datetime(temp_df['Date']).dt.date
    mask = (temp_df['Date'] > start_date) & (temp_df['Date'] <= end_date)
    temp_df = temp_df.loc[mask]
    temp_df.set_index('Date', inplace=True)
    # col_list = temp_df.columns
    # col_list.remove('Close')
    # temp_df.drop(, axis=1, inplace=True)
    temp_df.rename(columns={'Close':file_name.replace('.csv', '')}, inplace=True)
    temp_df = temp_df.loc[~temp_df.index.duplicated(keep='first')]
    # if(series):
    #     temp_df = temp_df[file_name.replace('.csv', '')].values
    # else:
    #     temp_df = temp_df[[file_name.replace('.csv', '')]]

    return temp_df

def sort_dict(x, reverse):
    return {k: v for k, v in sorted(x.items(), 
                                key=lambda item: item[1], reverse=reverse)}

def slice_dict(x, K):
    return dict(itertools.islice(x.items(), K))

def return_latest_data(file, date):
    df = pd.read_csv(file)
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    df = df[df["Date"]==date]
    return df

def clean_dict(x):
    new_x = {}
    for k, v in x.items():
        if(v!=float('nan')):
            new_x[k] = v
    return new_x