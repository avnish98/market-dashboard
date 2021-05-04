import json

def find_in_json(json_data, key, value):
    entry = None
    for j in json_data:
        if(j[key] == value):
            entry = j
            break
    return entry

def read_json(json_file):
    data = None
    with open(json_file, 'r') as infile:
        data = json.load(infile)
    return data

def write_json(json_data, json_file):
    with open(json_file, 'w') as outfile:
        json.dump(json_data, outfile, indent=4)