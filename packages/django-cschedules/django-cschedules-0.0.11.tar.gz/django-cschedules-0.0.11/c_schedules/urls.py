from django.conf.urls import url

from django.conf import settings
from .views import CreateCSchedulesView, UpdateCSchedulesView, LoadTimezonePlaceView

urlpatterns = [
    url(r'^create/$', CreateCSchedulesView.as_view(), name='cs_create'),
    url(r'^update/(?P<pk>[0-9]+)/$', UpdateCSchedulesView.as_view(), name='cs_update'),
    url(r'^timezone_place/(?P<timezone_value>\w+)/$', LoadTimezonePlaceView.as_view(), name='load_timezone_place'),
]

if getattr(settings, 'USE_ONLY_REST_URLS', False):
    from .rest.v1.urls import rest_urlpatterns

    urlpatterns = rest_urlpatterns
elif getattr(settings, 'USE_WITH_REST_URLS', False):
    from .rest.v1.urls import rest_urlpatterns

    urlpatterns += rest_urlpatterns
