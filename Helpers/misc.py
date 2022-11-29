def search_dict_value(dictionary, search_value, my_keys=''):
    output = []
    for key, value in dictionary.items():
        current_key = f'{my_keys}["{key}"]'
        if type(value) is dict:
            output += search_dict_value(value, search_value, current_key)
        elif value == search_value:
            output.append(current_key)

    return output


def search_dict_key(dictionary, search_value, my_keys=''):
    output = []
    for key, value in dictionary.items():
        current_key = f'{my_keys}["{key}"]'
        if type(value) is dict:
            output += search_dict_key(value, search_value, current_key)
        elif key == search_value:
            output.append(current_key)

    return output


