from django.conf import settings


EVENT_TYPES = getattr(settings, 'EVENT_TYPES', [])
