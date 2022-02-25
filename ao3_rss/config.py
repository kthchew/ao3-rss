import logging
from os import environ

def reload_config():
    number_of_chapters_in_feed = __get_int_for_option('AO3_CHAPTERS_IN_WORK_FEED', 1, 100, 3)
    number_of_works_in_feed = __get_int_for_option('AO3_WORKS_IN_SERIES_FEED', 1, 100, 3)

def __get_int_for_option(environment_var, min, max, default):
    option = environ.get(environment_var, default)
    try:
        option = int(option)
        if option > max:
            option = max
            logging.warning('Value greater than ' + str(max) + ' given for ' + environment_var + '. Setting to ' + str(max) + '.')
        elif option < min:
            raise(ValueError)
    except ValueError:
        option = default
        logging.error('Invalid value for ' + environment_var + ': expected integer between ' + str(min) + ' and ' + str(max) + '. Using default (' + str(default) + ')')
    return option

number_of_chapters_in_feed = __get_int_for_option('AO3_CHAPTERS_IN_WORK_FEED', 1, 100, 3)
number_of_works_in_feed = __get_int_for_option('AO3_WORKS_IN_SERIES_FEED', 1, 100, 3)
