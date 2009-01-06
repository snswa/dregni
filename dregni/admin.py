from django.contrib import admin
from dregni import models


class EventMetadataInline(admin.TabularInline):
    model = models.EventMetadata


class EventAdmin(admin.ModelAdmin):
    inlines = [EventMetadataInline]
    prepopulated_fields = {'slug': ['title']}
    fieldsets = (
        (None, {
            'fields': (('title', 'slug'), 'description', 'tags'),
        }),
        ('Scheduling', {
            'fields': (('start_date', 'start_time'), ('end_date', 'end_time')),
        }),
    )
    list_display = ('title', 'start_date', 'end_date', 'tags')
    search_fields = ('title', 'description', 'tags')

admin.site.register(models.Event, EventAdmin)
