import calendar
from datetime import timedelta
from itertools import groupby
from operator import attrgetter

from dregni.conf import settings


def event_time_cmp(this, that):
    if this.start_time is None and that.start_time is None:
        return 0
    if this.start_time is None:
        return -1
    if that.start_time is None:
        return 1
    return cmp(this.start_time, that.start_time)


def events_by_week_and_day(queryset, start_date, weeks, first_weekday=settings.FIRST_WEEKDAY):
    """Given a queryset of Event objects, return a list of [[day1, ..., day7], week2, ...].

    Each day is a dictionary with these key/value pairs:
        date = <date object>
        events = <list of events for individual day>
    """
    first_date = first_weekdate(start_date, first_weekday)
    last_date = first_date + timedelta(days=weeks * 7)
    # Build the week and day lists.
    current_date = first_date
    week_list = []
    day_map = {
        # date: day-dict,
    }
    for week_number in range(weeks):
        day_list = []
        for day in range(7):
            day_dict = dict(
                date=current_date,
                events=[],
            )
            day_list.append(day_dict)
            day_map[current_date] = day_dict
            current_date += timedelta(days=1)
        week_list.append(day_list)
    # Get all of the events, then group them by date and slot them in.
    all_events = queryset.filter(start_date__gte=first_date, start_date__lt=last_date)
    for date, grouper in groupby(all_events, attrgetter('start_date')):
        day_map[date]['events'].extend(sorted(grouper, event_time_cmp))
    #
    return week_list


def first_weekdate(start_date, first_weekday=settings.FIRST_WEEKDAY):
    """Return the first date in the week that start date falls within."""
    start_weekday = start_date.weekday()
    offset = (start_weekday - first_weekday) % 7
    return start_date - timedelta(days=offset)


def iterweekdays(first_weekday=settings.FIRST_WEEKDAY):
    c = calendar.Calendar()
    c.setfirstweekday(first_weekday)
    return c.iterweekdays()
