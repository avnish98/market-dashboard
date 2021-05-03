def find_in_json(json_data, key, value):
    entry = None
    for j in json_data:
        if(j[key] == value):
            entry = j
            break
    return entry