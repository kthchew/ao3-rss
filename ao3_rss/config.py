import logging
from os import environ


def reload_config():
    global number_of_chapters_in_feed, number_of_works_in_feed, block_explicit_works
    number_of_chapters_in_feed = __get_int_for_option('AO3_CHAPTERS_IN_WORK_FEED', 1, 100, 25)
    number_of_works_in_feed = __get_int_for_option('AO3_WORKS_IN_SERIES_FEED', 1, 100, 1)
    block_explicit_works = __get_bool_for_option('AO3_BLOCK_EXPLICIT', False)


def __get_int_for_option(environment_var: str, min_value: int, max_value: int, default: int):
    option = environ.get(environment_var, default)
    try:
        option = int(option)
        if option > max_value:
            option = max_value
            logging.warning(
                'Value greater than ' + str(max_value) + ' given for ' + environment_var + '. Setting to '
                + str(max_value) + '.'
            )
        elif option < min_value:
            raise ValueError
    except ValueError:
        option = default
        logging.error('Invalid value for ' + environment_var + ': expected integer between ' + str(min_value) + ' and '
                      + str(max_value) + '. Using default (' + str(default) + ')')
    return option


def __get_bool_for_option(environment_var: str, default: bool):
    option = environ.get(environment_var, default)
    if isinstance(option, bool):
        return option

    return option.lower() == 'true'


number_of_chapters_in_feed = __get_int_for_option('AO3_CHAPTERS_IN_WORK_FEED', 1, 100, 25)
number_of_works_in_feed = __get_int_for_option('AO3_WORKS_IN_SERIES_FEED', 1, 100, 1)
block_explicit_works = __get_bool_for_option('AO3_BLOCK_EXPLICIT', False)
