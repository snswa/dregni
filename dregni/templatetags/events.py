from django import template
register = template.Library()

from dregni import models


class EventListNode(template.Node):
    def __init__(self, func, reference_day, num_events, num_days, context_var):
        self.func = func
        self.reference_day = template.Variable(reference_day)
        self.num_events = template.Variable(num_events)
        self.num_days = template.Variable(num_days)
        self.context_var = context_var

    def render(self, context):
        reference_day = self.reference_day.resolve(context)
        num_events = self.num_events.resolve(context)
        num_days = self.num_days.resolve(context)
        qs = self.func(reference_day, num_days)
        context[self.context_var] = qs[:num_events]
        return ''


class EventYearsNode(template.Node):
    def __init__(self, context_var):
        self.context_var = context_var

    def render(self, context):
        context[self.context_var] = self.get_years()
        return ''

    def get_years(self):
        for date in models.Event.objects.dates('start_date', 'year'):
            yield date.year


def do_events_before_day(parser, token):
    """
    Retrieves a list of ``Event`` objects that occur after a specified day.

    Usage::

       {% events_before_day [object] [num] as [varname] %}

    Example::

        {% events_before_day today 5 as upcoming_event_list %}
    """
    bits = token.contents.split()
    if len(bits) != 5:
        raise template.TemplateSyntaxError(_('%s tag requires exactly four arguments') % bits[0])
    if bits[3] != 'as':
        raise template.TemplateSyntaxError(_("third argument to %s tag must be 'as'") % bits[0])
    nums = bits[2].split(',')
    if len(nums) == 1:
        # If a number of days aren't provided, don't limit it
        nums.append('0')
    return EventListNode(models.Event._default_manager.before_date,
                         bits[1], nums[0], nums[1], bits[4])


def do_events_after_day(parser, token):
    """
    Retrieves a list of ``Event`` objects that occur after a specified day.

    Usage::

       {% events_after_day [object] [num_events] as [varname] %}

           or

       {% events_after_day [object] [num_events],[num_days] as [varname] %}

    Examples::

        {% events_after_day today 5 as upcoming_event_list %}

        {% events_after_day today 5,30 as upcoming_event_list %}
    """
    bits = token.contents.split()
    if len(bits) != 5:
        raise template.TemplateSyntaxError(_('%s tag requires exactly four arguments') % bits[0])
    if bits[3] != 'as':
        raise template.TemplateSyntaxError(_("third argument to %s tag must be 'as'") % bits[0])
    nums = bits[2].split(',')
    if len(nums) == 1:
        # If a number of days aren't provided, don't limit it
        nums.append('0')
    return EventListNode(models.Event._default_manager.after_date,
                         bits[1], nums[0], nums[1], bits[4])

def do_get_event_years(parser, token):
    """
    Retrieves a list of ``Event`` objects that occur after a specified day.

    Usage::

       {% get_event_years as [varname] %}

    Example::

        {% get_event_years as years %}
    """
    bits = token.contents.split()
    if len(bits) != 3:
        raise template.TemplateSyntaxError(_('%s tag requires exactly two arguments') % bits[0])
    if bits[1] != 'as':
        raise template.TemplateSyntaxError(_("first argument to %s tag must be 'as'") % bits[0])
    return EventYearsNode(bits[2])

register.tag('events_before_day', do_events_before_day)
register.tag('events_after_day', do_events_after_day)
register.tag('get_event_years', do_get_event_years)
