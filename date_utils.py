import calendar
from datetime import date


def get_end_of_month(thedate):
    """


    :type thedate: date
    :rtype : date
    """
    last_day_of_month = calendar.monthrange(thedate.year, thedate.month)[1]
    return date(thedate.year, thedate.month, last_day_of_month)


def get_start_of_month(thedate):
    """


    :type thedate: date
    :rtype : date
    """
    return date(thedate.year, thedate.month, 1)