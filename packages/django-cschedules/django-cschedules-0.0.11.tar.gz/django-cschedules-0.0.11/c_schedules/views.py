from django.http import JsonResponse
from django.urls import reverse
from django.views import View
from extra_views import CreateWithInlinesView, InlineFormSet
from extra_views import UpdateWithInlinesView

from .models import CSchedules, CSchedulesDays
from .source import DAY_CHOICE, VAR_BY_COUNTRY
from .forms import CSchedulesForm


class CSchedulesDaysInline(InlineFormSet):
    model = CSchedulesDays
    fields = ['day_number', 'start_time', 'end_time']
    extra = 1
    form_class = CSchedulesForm

    def get_formset_kwargs(self):
        kwargs = super().get_formset_kwargs()

        if 'data' in kwargs.keys():
            kwargs['data'] = kwargs['data'].dict()

        if self.request.method == 'POST':
            kwargs['save_as_new'] = True

        return kwargs


class BaseCSchedulesView:
    model = CSchedules
    inlines = [CSchedulesDaysInline]
    fields = ['title', 'timezone', 'timezone_place', 'use_work_weekend', 'use_holiday']

    def get_context_data(self, **kwargs):
        ctx = super(BaseCSchedulesView, self).get_context_data(**kwargs)
        ctx['days'] = DAY_CHOICE
        ctx['hour_range'] = range(0, 24)
        return ctx

    def get_success_url(self):
        return reverse('cs_update', args=(self.object.id,))

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST.dict(),
                'files': self.request.FILES,
            })
        return kwargs


class CreateCSchedulesView(BaseCSchedulesView, CreateWithInlinesView):
    template_name = 'c_schedules/create.html'

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def forms_valid(self, form, inlines):
        resp = super().forms_valid(form, inlines)

        # attach owner if exist
        user = self.request.user
        self.object.owner = user if user.is_authenticated() else None
        self.object.save()

        return resp


class UpdateCSchedulesView(BaseCSchedulesView, UpdateWithInlinesView):
    template_name = 'c_schedules/update.html'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # delete old CSchedulesDays
        self.object.days.all().delete()

        return super(UpdateCSchedulesView, self).post(request, *args, **kwargs)


class LoadTimezonePlaceView(View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        area = VAR_BY_COUNTRY.get(kwargs.get('timezone_value'), [])
        return JsonResponse({
            'results': [''] + list(area.keys())
        })
