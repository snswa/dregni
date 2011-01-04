import calendar

from django.conf import settings


# Set this to a constant from the 'calendar' module, or the name of a constant.
FIRST_WEEKDAY = getattr(settings, 'FIRST_WEEKDAY', calendar.MONDAY)
if isinstance(FIRST_WEEKDAY, basestring):
    FIRST_WEEKDAY = getattr(calendar, FIRST_WEEKDAY.upper())
if not isinstance(FIRST_WEEKDAY, int):
    raise ValueError('FIRST_WEEKDAY could not be resolved to an integer.')
