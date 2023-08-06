from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.dateparse import parse_time

from .source import RUSSIA, CIS, OTHER_COUNTRIES, DAY_CHOICE


class CSchedules(models.Model):
    TIMEZONE_NAME_CHOICES = (
        (RUSSIA, 'Россия'),
        (CIS, 'СНГ'),
        (OTHER_COUNTRIES, 'Страны мира'),
    )

    title = models.CharField(verbose_name='Заголовок расписания', max_length=100)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='c_shedules_list', verbose_name='Создатель',
        blank=True, null=True
    )

    timezone = models.CharField(verbose_name='Часовой пояс', max_length=3, choices=TIMEZONE_NAME_CHOICES)
    timezone_place = models.CharField(verbose_name='Местоположение', max_length=100)

    use_work_weekend = models.BooleanField(verbose_name='Учитывать рабочие выходные', default=True)
    use_holiday = models.BooleanField(verbose_name='Учитывать праздничные дни', default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Планировщик расписания'
        verbose_name_plural = 'Список планировщиков расписаний'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class CSchedulesDays(models.Model):
    c_schedules = models.ForeignKey(CSchedules, related_name='days', verbose_name='Планировщик')

    day_number = models.IntegerField(verbose_name='Номер дня', validators=[MinValueValidator(1), MaxValueValidator(7)])

    start_time = models.TimeField(verbose_name='Старт', validators=[
        MinValueValidator(parse_time("00:00"), MaxValueValidator(parse_time("23:00")))])
    end_time = models.TimeField(
        verbose_name='Конец', validators=[
            MinValueValidator(parse_time("01:00")),
            MaxValueValidator(parse_time("23:59"))]
    )

    @property
    def day_name(self):
        return dict(DAY_CHOICE).get(self.day_number)

    class Meta:
        verbose_name = 'День в расписании'
        verbose_name_plural = 'Список дней в расписании'
        unique_together = ['c_schedules', 'day_number', 'start_time', 'end_time']
        ordering = ['day_number']

    def __str__(self):
        return "{0} - start:{1}; end:{2}".format(self.day_number, self.start_time, self.end_time)
