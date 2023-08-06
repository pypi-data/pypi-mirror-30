"""Parse the date from various formats.
"""
__copyright__ = "Copyright (C) 2014-2016  Martin Blais"
__license__ = "GNU GPLv2"

import datetime
import dateutil.parser


def iter_dates(start_date, end_date):
    """Yield all the dates between 'start_date' and 'end_date'.

    Args:
      start_date: An instance of datetime.date.
      end_date: An instance of datetime.date.
    Yields:
      Instances of datetime.date.
    """
    oneday = datetime.timedelta(days=1)
    date = start_date
    while date < end_date:
        yield date
        date += oneday


def parse_date_liberally(string, parse_kwargs_dict=None):
    """Parse arbitrary strings to dates.

    This function is intended to support liberal inputs, so that we can use it
    in accepting user-specified dates on command-line scripts.

    Args:
      string: A string to parse.
      parse_kwargs_dict: Dict of kwargs to pass to dateutil parser.
    Returns:
      A datetime.date object.
    """
    # At the moment, rely on the most excellent dateutil.
    if parse_kwargs_dict is None:
        parse_kwargs_dict = {}
    return dateutil.parser.parse(string, **parse_kwargs_dict).date()


def render_ofx_date(dtime):
    """Render a datetime to the OFX format.

    Args:
      dtime: A datetime.datetime instance.
    Returns:
      A string, rendered to milliseconds.
    """
    return '{}.{:03d}'.format(dtime.strftime('%Y%m%d%H%M%S'),
                              int(dtime.microsecond / 1000))


def next_month(date):
    """Compute the date at the beginning of the following month from the given date.

    Args:
      date: A datetime.date instance.
    Returns:
      A datetime.date instance, the first day of the month following 'date'.
    """
    # Compute the date at the beginning of the following month.
    year = date.year
    month = date.month + 1
    if date.month == 12:
        year += 1
        month = 1
    return datetime.date(year, month, 1)
