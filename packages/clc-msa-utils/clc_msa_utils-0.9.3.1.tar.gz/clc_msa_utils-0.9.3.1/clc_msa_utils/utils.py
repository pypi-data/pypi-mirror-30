from copy import deepcopy


def dict_replace_empty_values(in_dictionary,
                              processed_dicts=[],
                              process_none_values=False,
                              clone_dict=False,
                              remove_values=False,
                              replace_with=None):

    if type(in_dictionary) is not dict:
        raise Exception("Value provided must be a dictionary.")

    if clone_dict:
        in_dictionary = deepcopy(in_dictionary)

    keys_to_process = []

    for key in in_dictionary.keys():
        value = in_dictionary.get(key)
        if process_none_values and value is None:
            keys_to_process.append(key)
        elif type(value) is str and len(value.strip()) == 0:
            keys_to_process.append(key)
        elif type(value) is dict and value not in processed_dicts:
            processed_dicts.append(value)
            dict_replace_empty_values(value,
                                      processed_dicts=processed_dicts,
                                      process_none_values=process_none_values,
                                      clone_dict=False,
                                      remove_values=remove_values,
                                      replace_with=replace_with)

    for key_to_process in keys_to_process:
        if remove_values:
            in_dictionary.pop(key_to_process)
        else:
            in_dictionary[key_to_process] = replace_with

    return in_dictionary
