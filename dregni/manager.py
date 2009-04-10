import datetime
from django.db import models
from django.contrib.sites.models import Site


class EventManager(models.Manager):
    def for_current_site(self):
        return self.filter(site=Site.objects.get_current())

