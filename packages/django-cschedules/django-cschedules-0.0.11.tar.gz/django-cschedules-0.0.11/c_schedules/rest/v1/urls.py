from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from .views import CSchedulesViewSet

cs_list = CSchedulesViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

cs_detail = CSchedulesViewSet.as_view({
    'put': 'update',
    'delete': 'destroy'
})

urlpatterns = [
    url(r'^api_list/$', cs_list),
    url(r'^api_list/(?P<pk>[0-9]+)/$', cs_detail),
]

rest_urlpatterns = format_suffix_patterns(urlpatterns)
