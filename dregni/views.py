import datetime
import vobject
from django import http
from django.contrib.sites.models import Site


def icalendar(request, queryset):
    ical = vobject.iCalendar()
    ical.add('method').value = 'PUBLISH'
    site = Site.objects.get_current()
    for event in queryset.all():
        vevent = ical.add('vevent')
        vevent.add('uid').value = '%s.%s@%s' % (
            event.start_date.strftime('%Y-%m-%d'),
            event.slug.encode('utf8'),
            site.domain)
        if event.start_time:
            start_time = event.start_time
        else:
            start_time = datetime.time()
        start_date = datetime.datetime.combine(event.start_date, start_time)
        vevent.add('dtstart').value = start_date
        vevent.add('dtstamp').value = start_date
        if event.end_date:
            if event.end_time:
                end_time = event.end_time
            else:
                end_time = datetime.time(23, 59)
            end_date = datetime.datetime.combine(event.end_date, end_time)
        else:
            end_date = start_date
        vevent.add('dtend').value = end_date
        vevent.add('summary').value = event.title
        vevent.add('description').value = event.description
        
        for meta in event.metadata.all():
            if meta.type == 'place':
                vevent.add('location').value = meta.text
        vevent.add('categories').value = event.tags.split()

    return http.HttpResponse(ical.serialize(), mimetype='text/calendar')

