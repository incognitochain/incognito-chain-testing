from datetime import datetime


def get_current_date_time(my_format=None):
    if my_format is None:
        my_format = "%d%m%y%H%M%S.log"
    return datetime.now().strftime(my_format)
