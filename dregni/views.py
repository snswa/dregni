import datetime
import vobject
from django import http
from django.contrib.sites.models import Site
from django.conf import settings


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
        event_url = event.start_date.strftime(settings.EVENT_URL_FORMAT).lower()
        vevent.add('url').value = event_url
        if False and event.start_time:
            start_datetime = datetime.datetime.combine(event.start_date,
                                                       event.start_time)
            vevent.add('dtstart').value = start_datetime
            vevent.add('dtstamp').value = start_datetime
        else:
            vevent.add('dtstart').value = event.start_date
            vevent.dtstart.value_param = 'DATE'
            vevent.add('dtstamp').value = datetime.datetime.combine(event.start_date,
                                                                    datetime.time())
        if event.end_date:
            if False and event.end_time:
                vevent.add('dtend').value = datetime.datetime.combine(event.end_date,
                                                                      event.end_time)
            else:
                vevent.add('dtend').value = event.end_date + datetime.timedelta(days=1)
                vevent.dtend.value_param = 'DATE'
        vevent.add('summary').value = event.title
        vevent.add('description').value = event.description
        
        for meta in event.metadata.all():
            if meta.type == 'place':
                vevent.add('location').value = meta.text
        vevent.add('categories').value = event.tags.split()

    return http.HttpResponse(ical.serialize(), mimetype='text/calendar')

