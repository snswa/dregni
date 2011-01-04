import calendar
import datetime
import time
import vobject

from django.contrib.sites.models import Site
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, Http404, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, RequestContext

from dregni.forms import EventForm
from dregni.models import Event
from dregni.utils import events_by_week_and_day, iterweekdays


def _group_bridge_base(request):
    group = getattr(request, 'group', None)
    if group:
        bridge = request.bridge
        group_base = bridge.group_base_template()
    else:
        bridge = None
        group_base = None
    return (group, bridge, group_base)


def index(request, start_date=None, weeks=None, filter_qs=lambda qs: qs,
          template_name='dregni/index.html', extra_context=None, **kwargs
          ):
    extra_context = extra_context or {}
    group, bridge, group_base = _group_bridge_base(request)
    #
    # Queryset.
    if group:
        queryset = group.content_objects(Event)
    else:
        queryset = Event.objects.filter(content_type=None, object_id=None)
    event_list = filter_qs(queryset)
    #
    template_context = {
        'event_list': event_list,
        'group': group,
        'group_base': group_base,
    }
    if callable(start_date):
        start_date = start_date()
    if start_date is not None:
        template_context.update({
            'day_abbr': [calendar.day_abbr[idx] for idx in iterweekdays()],
            'day_name': [calendar.day_name[idx] for idx in iterweekdays()],
            'start_date': start_date,
            'today': datetime.date.today(),
            'weeks': events_by_week_and_day(event_list, start_date, weeks),
        })
    template_context.update(extra_context)
    return render_to_response(template_name, template_context, RequestContext(request))


def event(request, event_id, slug=None,
          template_name='dregni/event.html', extra_context=None, **kwargs
          ):
    extra_context = extra_context or {}
    group, bridge, group_base = _group_bridge_base(request)
    #
    # Queryset.
    if group:
        queryset = group.content_objects(Event)
    else:
        queryset = Event.objects.filter(content_type=None, object_id=None)
    try:
        event = queryset.get(pk=event_id)
    except Event.DoesNotExist:
        raise Http404
    #
    template_context = {
        'event': event,
        'group': group,
        'group_base': group_base,
    }
    template_context.update(extra_context)
    return render_to_response(template_name, template_context, RequestContext(request))


def delete(request, event_id,
           event_delete_predicate=lambda request, event: True,
           template_name='dregni/delete.html', extra_context=None, **kwargs
           ):
    extra_context = extra_context or {}
    group, bridge, group_base = _group_bridge_base(request)
    #
    # Get the event specified.
    if group:
        queryset = group.content_objects(Event)
    else:
        queryset = Event.objects.filter(content_type=None, object_id=None)
    try:
        event = queryset.get(pk=event_id)
    except Event.DoesNotExist:
        raise Http404
    #
    # Enforce predicate.
    if not event_delete_predicate(request, event):
        return HttpResponseForbidden('You do not have permission to delete events.')
    #
    if request.method == 'POST':
        if request.POST.get('delete') == '1':
            event.delete()
            if group:
                url = bridge.reverse('dregni_index', group)
            else:
                url = reverse('dregni_index')
        else:
            url = event.get_absolute_url()
        return HttpResponseRedirect(url)
    #
    template_context = {
        'event': event,
        'group': group,
        'group_base': group_base,
    }
    template_context.update(extra_context)
    return render_to_response(template_name, template_context, RequestContext(request))


def edit(request, event_id=None,
         event_edit_predicate=lambda request, event: True,
         form_class=EventForm,
         template_name='dregni/edit.html', extra_context=None, **kwargs
         ):
    extra_context = extra_context or {}
    group, bridge, group_base = _group_bridge_base(request)
    #
    # Get the event if one was specified.
    if event_id is None:
        event = None
    else:
        if group:
            queryset = group.content_objects(Event)
        else:
            queryset = Event.objects.filter(content_type=None, object_id=None)
        try:
            event = queryset.get(pk=event_id)
        except Event.DoesNotExist:
            raise Http404
    #
    # Enforce predicate.
    if not event_edit_predicate(request, event):
        return HttpResponseForbidden('You do not have permission to edit events.')
    #
    if request.method == 'POST':
        event_form = form_class(request.POST, instance=event)
        if event_form.is_valid():
            event = event_form.save(commit=False)
            if not event.pk:
                event.site = Site.objects.get_current()
                event.group = group
                event.creator = request.user
            else:
                event.modifier = request.user
            event.save()
            return HttpResponseRedirect(event.get_absolute_url())
    elif request.method == 'GET':
        event_form = form_class(instance=event)
    #
    template_context = {
        'event': event,
        'event_form': event_form,
        'group': group,
        'group_base': group_base,
    }
    template_context.update(extra_context)
    return render_to_response(template_name, template_context, RequestContext(request))


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

    return HttpResponse(ical.serialize(), mimetype='text/calendar')

