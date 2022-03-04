"""
Gets the configuration for the app.
"""
import logging
from os import environ


def __get_int_for_option(environment_var: str, min_value: int, max_value: int, default: int):
    option = environ.get(environment_var, default)
    try:
        option = int(option)
        if option > max_value:
            option = max_value
            logging.warning('Value greater than %d given for %s. Setting to %d.', max_value, environment_var, max_value)
        elif option < min_value:
            raise ValueError
    except ValueError:
        option = default
        logging.error(
            'Invalid value for %s: expected integer between %d and %d. Using default (%s)',
            environment_var, min_value, max_value, default
        )
    return option


def __get_bool_for_option(environment_var: str, default: bool):
    option = environ.get(environment_var, default)
    if isinstance(option, bool):
        return option

    return option.lower() == 'true'


NUMBER_OF_CHAPTERS_IN_FEED = __get_int_for_option('AO3_CHAPTERS_IN_WORK_FEED', 1, 100, 25)
NUMBER_OF_WORKS_IN_FEED = __get_int_for_option('AO3_WORKS_IN_SERIES_FEED', 1, 100, 1)
BLOCK_EXPLICIT_WORKS = __get_bool_for_option('AO3_BLOCK_EXPLICIT', False)
