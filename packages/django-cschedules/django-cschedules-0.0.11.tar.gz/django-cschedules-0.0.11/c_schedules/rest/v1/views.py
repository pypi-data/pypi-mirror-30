from django.contrib import messages
from rest_framework.viewsets import ModelViewSet

from .serializers import CShedulesSerializer
from ...models import CSchedules


class CSchedulesViewSet(ModelViewSet):
    serializer_class = CShedulesSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated():
            return self.request.user.c_shedules_list.all()
        else:
            return CSchedules.objects.all()

    def perform_create(self, serializer):
        instance = serializer.save()

        messages.add_message(
            self.request, messages.SUCCESS,
            'Schedules with title "{0}" success created'.format(instance.title)
        )

    def perform_update(self, serializer):
        instance = serializer.save()

        messages.add_message(
            self.request, messages.SUCCESS,
            'Schedules with title "{0}" success updated'.format(instance.title)
        )

    def perform_destroy(self, instance):
        title = instance.title

        super().perform_destroy(instance)

        messages.add_message(
            self.request, messages.SUCCESS,
            'Schedules with title "{0}" success deleted'.format(title)
        )
