"""

>>> import calendar
>>> from datetime import date, time
>>> from django.contrib.auth.models import User
>>> from django.contrib.sites.models import Site
>>> from dregni.models import Event
>>> from dregni.utils import events_by_week_and_day, iterweekdays

>>> list(iterweekdays(calendar.SUNDAY))
[6, 0, 1, 2, 3, 4, 5]

    SU MO TU WE TH FR SA
DEC 26 27 28 29 30 31  1   <-- ignore these
JAN  2  3  4  5  6  7  8   <== include these
JAN  9 10 11 12 13 14 15   <==
JAN 16 17 18 19 20 21 22   <--

>>> site = Site.objects.get(pk=1)
>>> user = User(username='alice')
>>> user.save()
>>> Event(site=site, creator=user, title='no', start_date=date(2011, 1, 1)).save()
>>> Event(site=site, creator=user, title='yes', start_date=date(2011, 1, 2)).save()
>>> Event(site=site, creator=user, title='yes', start_date=date(2011, 1, 15)).save()
>>> Event(site=site, creator=user, title='yes', start_date=date(2011, 1, 15), start_time=time(23, 59, 59)).save()
>>> Event(site=site, creator=user, title='no', start_date=date(2011, 1, 16)).save()

>>> queryset = Event.objects.all()
>>> weeks = events_by_week_and_day(
...     Event.objects.all(),
...     start_date=date(2011, 1, 5),
...     weeks=2,
...     first_weekday=calendar.SUNDAY,
...     )
>>> weeks[0][0]['date'].isoformat()
'2011-01-02'
>>> len(weeks[0][0]['events'])
1
>>> len(weeks[0][1]['events'])
0
>>> len(weeks[1][6]['events'])
2
>>> weeks[1][6]['events'][-1].start_time.isoformat()
'23:59:59'
>>> for week in weeks:
...     for day in week:
...         for event in day['events']:
...             assert event.start_date == day['date']
...             assert event.title == 'yes'

"""
