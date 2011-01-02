import datetime

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.core.urlresolvers import NoReverseMatch, reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from dregni.conf import settings
from dregni import manager
from tagging.fields import TagField


class Event(models.Model):
    site = models.ForeignKey(Site)
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'))

    start_date = models.DateField(_('start date'))
    start_time = models.TimeField(_('start time'), null=True, blank=True)
    end_date = models.DateField(_('end date'), null=True, blank=True)
    end_time = models.TimeField(_('end time'), null=True, blank=True)

    tags = TagField(_('tags'))

    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    group = generic.GenericForeignKey("content_type", "object_id")

    creator = models.ForeignKey(User, blank=True, null=True, related_name='dregni_events_created')
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modifier = models.ForeignKey(User, blank=True, null=True, related_name='dregni_events_modified')
    modified = models.DateTimeField(_('modified'), auto_now=True, db_index=True)

    objects = manager.EventManager()

    class Meta:
        ordering = ('start_date', 'start_time', 'end_date', 'end_time')

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        kwargs = {
            'event_id': self.id,
            'slug': slugify(self.title),
        }
        group = self.group
        try:
            if group:
                return group.content_bridge.reverse('dregni_event_slug', group, kwargs)
            else:
                return reverse('dregni_event_slug', kwargs=kwargs)
        except NoReverseMatch:
            return None

    def is_all_day(self):
        return not self.start_time

    def get_start_datetime(self):
        if self.start_time:
            return datetime.datetime.combine(self.start_date, self.start_time)
        return datetime.datetime.combine(self.start_date, datetime.time())

    def get_end_datetime(self):
        if self.end_date and self.end_time:
            return datetime.datetime.combine(self.end_date, self.end_time)
        elif self.end_date:
            return datetime.datetime.combine(self.end_date + datetime.timedelta(1), datetime.time())
        return self.get_start_datetime()

    def is_past(self):
        return self.get_end_datetime() < datetime.datetime.now()

    def is_current(self):
        return self.get_start_datetime() < datetime.datetime.now() < self.get_end_datetime()

    def is_future(self):
        return self.get_start_datetime() > datetime.datetime.now()

    def previous_events(self, num=5):
        """
        Retrieves the next set of events after the current one.
        """
        same_day = models.Q(start_date=self.start_date,
                            start_time=self.start_time)
        prior_days = models.Q(start_date__lt=self.start_date)
        qs = self._default_manager.filter(same_day | prior_days)
        return qs[num]

    def next_events(self, num=5):
        """
        Retrieves the next set of events after the current one.
        """
        same_day = models.Q(start_date=self.start_date,
                            start_time=self.start_time)
        future_days = models.Q(start_date__gt=self.start_date)
        qs = self._default_manager.filter(same_day | future_days)
        return qs.order_by('-end_date', '-end_time',
                           '-start_date', '-start_time')[num]
