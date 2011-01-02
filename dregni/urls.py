from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('dregni.views',
    url(
        name='dregni_index',
        regex=r'^$',
        view='index',
    ),
    url(
        name='dregni_event_create',
        regex=r'^create/$',
        view='edit',
        kwargs={
            'template_name': 'dregni/create.html',
        },
    ),
    url(
        name='dregni_event',
        regex=r'^(?P<event_id>\d+)/$',
        view='event',
    ),
    url(
        name='dregni_event_delete',
        regex=r'^(?P<event_id>\d+)/delete/$',
        view='delete',
    ),
    url(
        name='dregni_event_edit',
        regex=r'^(?P<event_id>\d+)/edit/$',
        view='edit',
    ),
    url(
        name='dregni_event_slug',
        regex=r'^(?P<event_id>\d+)/(?P<slug>[\w_-]+)/$',
        view='event',
    ),
)
