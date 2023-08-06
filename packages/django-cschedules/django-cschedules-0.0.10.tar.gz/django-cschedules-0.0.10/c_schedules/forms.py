from django import forms
from .models import CSchedules
from .source import VAR_BY_COUNTRY


class CSchedulesForm(forms.ModelForm):
    def clean_timezone(self):
        tz = self.cleaned_data.get('timezone')

        if tz not in VAR_BY_COUNTRY.keys():
            raise forms.ValidationError('Некорректное значение часового пояса')

        return tz

    def clean_timezone_place(self):
        tz = self.cleaned_data.get('timezone')
        tz_place = self.cleaned_data.get('timezone_place')

        if tz_place not in VAR_BY_COUNTRY[tz]:
            raise forms.ValidationError('Некорректное значение местоположения')

        return tz_place

    class Meta:
        model = CSchedules
        fields = ('title', 'timezone', 'timezone_place', 'use_work_weekend', 'use_holiday')
