import datetime
from django.db import models


class EventManager(models.Manager):
    def for_date(self, date):
        return self.filter(start_date__lt=date, end_date__gt=date)

    def before_date(self, date, num_days=None):
        qs = self.filter(start_date__lt=date)
        if num_days:
            qs = qs.filter(start_date__gt=date-datetime.timedelta(days=num_days))
        return qs.order_by('-end_date', '-end_time', '-start_date', '-start_time')

    def after_date(self, date, num_days=None):
        qs = self.filter(start_date__gt=date)
        if num_days:
            qs = qs.filter(start_date__lt=date+datetime.timedelta(days=num_days))
        return qs

