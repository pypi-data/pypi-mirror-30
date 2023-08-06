from django.contrib import admin
from django.conf import settings

from .models import CSchedulesDays, CSchedules
from .source import DAY_CHOICE

if getattr(settings, 'CS_USE_IN_ADMIN_PANEL', True):
    class CShedulesDaysInline(admin.TabularInline):
        model = CSchedulesDays
        extra = 3


    @admin.register(CSchedules)
    class CShedulesAdmin(admin.ModelAdmin):
        list_display = ['title', 'owner', 'use_work_weekend', 'use_holiday', 'updated_at', 'day_count']
        list_filter = ['title', 'use_holiday', 'use_work_weekend']
        search_fields = ['title', 'owner', 'use_work_weekend', 'use_holiday', 'day_count']
        inlines = [CShedulesDaysInline]

        add_form_template = 'admin/c_shedules/change_form.html'
        change_form_template = 'admin/c_shedules/change_form.html'

        def day_count(self, obj):
            return obj.days.count()

        day_count.short_description = 'Количество дней'

        def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
            extra_context = {
                'days': DAY_CHOICE,
                'hour_range': range(0, 24)
            }
            return super().changeform_view(request, object_id=object_id, form_url=form_url, extra_context=extra_context)
