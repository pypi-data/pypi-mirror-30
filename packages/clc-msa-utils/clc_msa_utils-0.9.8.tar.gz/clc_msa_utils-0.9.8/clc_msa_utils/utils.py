import logging
from copy import deepcopy
from decimal import Decimal

logger = logging.getLogger('utils')


def dict_replace_empty_values(in_dictionary,
                              processed_dicts=[],
                              process_none_values=False,
                              clone_dict=False,
                              remove_values=False,
                              replace_with=None,
                              replace_float_with_decimal=False):
    if type(in_dictionary) is not dict:
        raise Exception("Value provided must be a dictionary.")

    if clone_dict:
        in_dictionary = deepcopy(in_dictionary)

    keys_to_process = []

    for key in in_dictionary.keys():
        value = in_dictionary.get(key)
        if process_none_values and value is None:
            keys_to_process.append(key)
        if type(value) is float:
            if replace_float_with_decimal:
                in_dictionary[key] = Decimal(str(value))
        elif type(value) is str and len(value.strip()) == 0:
            keys_to_process.append(key)
        elif type(value) is dict and value not in processed_dicts:
            processed_dicts.append(value)
            dict_replace_empty_values(value,
                                      processed_dicts=processed_dicts,
                                      process_none_values=process_none_values,
                                      clone_dict=False,
                                      remove_values=remove_values,
                                      replace_with=replace_with,
                                      replace_float_with_decimal=replace_float_with_decimal)

    for key_to_process in keys_to_process:
        if remove_values:
            in_dictionary.pop(key_to_process)
        else:
            in_dictionary[key_to_process] = replace_with

    return in_dictionary


def log_dict_types(a_dict, prefix="", types=None, use_logger=logger, print_no_type_message=False):
    was_logged = False
    for key in a_dict.keys():
        if prefix:
            fq_key = "{0}.{1}".format(prefix, key)
        else:
            fq_key = "{0}".format(key)
        value = a_dict.get(key)
        value_type = type(value).__name__
        if not types or value_type in types:
            use_logger.info("'self.{0}' is a '{1}'".format(fq_key, value_type))
            was_logged = True
        if type(value) is dict:
            log_dict_types(value, prefix=fq_key, types=types, use_logger=use_logger)
    if not was_logged:
        if prefix:
            self_prefix = "self."
        else:
            self_prefix = "self"
        if print_no_type_message:
            use_logger.info("'{0}' has no type in {1}".format("{0}{1}".format(self_prefix, prefix), str(types)))
