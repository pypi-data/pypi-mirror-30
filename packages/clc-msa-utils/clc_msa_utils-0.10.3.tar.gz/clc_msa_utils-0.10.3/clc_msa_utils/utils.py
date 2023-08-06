import logging
from copy import deepcopy
from decimal import Decimal

logger = logging.getLogger('utils')


def dict_replace_empty_values(in_dictionary,
                              process_none_values=False,
                              clone_dict=False,
                              remove_values=False,
                              replace_with=None,
                              replace_float_with_decimal=False):
    if type(in_dictionary) is not dict:
        raise Exception("Value provided must be a dictionary.")

    if clone_dict:
        logger.debug("Cloning dictionary")
        in_dictionary = deepcopy(in_dictionary)

    keys_to_process = []

    for key in in_dictionary.keys():
        value = in_dictionary.get(key)
        logger.debug("Processing key '{0}' of type '{1}'".format(key, type(value).__name__))
        if process_none_values and value is None:
            logger.debug("Adding key '{0}' to keys to process.".format(key))
            keys_to_process.append(key)
        if type(value) is float:
            if replace_float_with_decimal:
                logger.debug("Converting '{0}' to Decimal".format(key))
                in_dictionary[key] = Decimal(str(value))
            else:
                logger.debug("NOT converting '{0}' to Decimal".format(key))
        elif type(value) is str:
            if len(value.strip()) == 0:
                logger.debug("Adding key '{0}' to keys to process.".format(key))
                keys_to_process.append(key)
            else:
                logger.debug("Value for key '{0}' is not blank.".format(key))
        elif type(value) is dict:
            logger.debug("Calling dict_replace_empty_values for keys '{0}'.".format(key))
            dict_replace_empty_values(value,
                                      process_none_values=process_none_values,
                                      clone_dict=False,
                                      remove_values=remove_values,
                                      replace_with=replace_with,
                                      replace_float_with_decimal=replace_float_with_decimal)
        else:
            logger.debug("No special handing required for key '{0}' for its type.".format(key))

    for key_to_process in keys_to_process:
        if remove_values:
            logger.debug("Removing key '{0}'.".format(key_to_process))
            in_dictionary.pop(key_to_process)
        else:
            logger.debug("Replacing key '{0}' with '{1}'.".format(key_to_process, replace_with))
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
