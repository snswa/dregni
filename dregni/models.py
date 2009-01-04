from django.db import models
from django.utils.translation import ugettext_lazy as _
from tagging.fields import TagField

from dregni import manager


class Event(models.Model):
    title = models.CharField(_('title'), max_length=255)
    slug = models.SlugField(_('slug'))
    description = models.TextField(_('description'))

    start_date = models.DateField(_('start date'))
    start_time = models.TimeField(_('start time'), null=True, blank=True)
    end_date = models.DateField(_('end date'), null=True, blank=True)
    end_time = models.TimeField(_('end time'), null=True, blank=True)

    tags = TagField(_('tags'))

    objects = manager.EventManager()

    class Meta:
        ordering = ('start_date', 'start_time', 'end_date', 'end_time')
        unique_together = ('start_date', 'slug')

    def __unicode__(self):
        return self.title

    def is_all_day(self):
        return not self.start_time

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


class EventMetadata(models.Model):
    LINK = 'link'
    PLACE = 'place'
    GROUP = 'group'
    PERSON = 'person'
    CHOICES = (
        (LINK, _('link')),
        (PLACE, _('place')),
        (GROUP, _('group')),
        (PERSON, _('person')),
    )
    event = models.ForeignKey(Event, verbose_name=_('event'),
                              related_name='metadata')
    type = models.CharField(_('type'), max_length=20, choices=CHOICES)
    text = models.CharField(_('text'), max_length=255)
    url = models.URLField(_('URL'), blank=True, verify_exists=False)

    def __unicode__(self):
        return self.text

