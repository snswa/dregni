from django import forms

from dregni.models import Event


class EventForm(forms.ModelForm):

    class Meta:
        model = Event
        exclude = (
            'site',
            'tags',
            'content_type',
            'object_id',
            'creator',
            'created',
            'modifier',
            'modified',
        )
