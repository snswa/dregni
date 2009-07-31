import datetime
import time
import vobject
from django import http
from django.contrib.sites.models import Site
from django.conf import settings
from django.http import HttpResponse, Http404
from django.template import loader, RequestContext
from django.db.models import Q


def archive_day(request, year, month, day, queryset, date_field,
        month_format='%b', day_format='%d', template_name=None,
        template_loader=loader, extra_context=None, allow_empty=True,
        context_processors=None, template_object_name='object',
        mimetype=None, allow_future=True,
        num_recent_days=90, num_upcoming_days=90,
        num_recent_events=5, num_upcoming_events=5):
    """
    Generic daily archive view.

    Templates: ``<app_label>/<model_name>_archive_day.html``
    Context:
        current_events:
            list of objects published that day
        day:
            (datetime) the day
        previous_day
            (datetime) the previous day
        next_day
            (datetime) the next day, or None if the current day is today
    """
    if extra_context is None: extra_context = {}
    try:
        date = datetime.date(*time.strptime(year+month+day, '%Y'+month_format+day_format)[:3])
    except ValueError:
        raise Http404

    model = queryset.model
    
    # Locate events for the given date
    current_events = queryset.filter(Q(end_date__isnull=True, start_date=date) | \
                                     Q(start_date__lte=date, end_date__gte=date))

    # Locate events in the immediate future
    upcoming_events = queryset.filter(start_date__gt=date)
    if num_upcoming_days:
        upcoming_events = upcoming_events.filter(start_date__lt=date + \
                                                 datetime.timedelta(days=num_upcoming_days))

    if not template_name:
        template_name = "%s/%s_archive_day.html" % (model._meta.app_label,
                                                    model._meta.object_name.lower())

    # Locate events in the recent past
    recent_events = queryset.filter(Q(end_date__isnull=True, start_date__lt=date) | \
                                    Q(end_date__lt=date))
    if num_recent_days:
        recent_events = recent_events.filter(start_date__gt=date - \
                                             datetime.timedelta(days=num_recent_days))
    recent_events = recent_events.extra(select={'_end_date': 'coalesce(end_date, start_date)'})
    recent_events = recent_events.order_by('-_end_date', '-end_time',
                                           '-start_date', '-start_time')

    t = template_loader.get_template(template_name)
    c = RequestContext(request, {
        '%s_list' % template_object_name: current_events,
        'day': date,
        'previous_day': date - datetime.timedelta(days=1),
        'next_day': date + datetime.timedelta(days=1),
        'upcoming_events': upcoming_events[:num_upcoming_events],
        'recent_events': recent_events[:num_recent_events],
    }, context_processors)
    for key, value in extra_context.items():
        if callable(value):
            c[key] = value()
        else:
            c[key] = value
    return HttpResponse(t.render(c), mimetype=mimetype)


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

