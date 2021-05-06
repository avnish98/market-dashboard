"""Utils module

This script contains utility/helper functions for read/write related queries.

It contains following functions
    * find_in_json: Finds entry in JSON where key = value and returns it as dict
    * read_json: Reads JSON file and returns it as list[dict]
    * write_json: Writes list[dict] as json
    * write_csv: Writes pandas DataFrame as CSV file
"""

import json
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