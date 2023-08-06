from django.contrib.auth.models import AnonymousUser
from rest_framework import serializers

from ...models import CSchedules, CSchedulesDays
from ...source import VAR_BY_COUNTRY


class CShedulesDaysSerializer(serializers.ModelSerializer):
    start_time = serializers.TimeField(format="%H:%M", required=True)
    end_time = serializers.TimeField(format="%H:%M", required=True)
    day_name = serializers.SerializerMethodField(read_only=True)

    def get_day_name(self, obj):
        return obj.day_name

    def validate(self, attrs):
        if attrs['start_time'] >= attrs['end_time']:
            raise serializers.ValidationError('end time should be longer than star time')

        return attrs

    class Meta:
        model = CSchedulesDays
        fields = ('id', 'day_number', 'day_name', 'start_time', 'end_time')
        read_only_fields = ('id',)


class CShedulesSerializer(serializers.ModelSerializer):
    days = CShedulesDaysSerializer(many=True, required=True)
    timezone_offset = serializers.SerializerMethodField(read_only=True)
    timezone_name = serializers.SerializerMethodField(read_only=True)

    def get_timezone_name(self, obj):
        return obj.get_timezone_display()

    def get_timezone_offset(self, obj):
        tz = obj.timezone
        tz_place = obj.timezone_place
        try:
            return VAR_BY_COUNTRY[tz][tz_place]
        except KeyError:
            return 'incorrent value'

    def validate_title(self, title):
        user = self._get_current_user()
        if user.is_authenticated():
            try:
                user.c_shedules_list.get(title=title)
                raise serializers.ValidationError(
                    'Schedule with title: :{0}" from the user: "{1}" already exist'.format(title, user)
                )
            except CSchedules.DoesNotExist:
                pass

        return title

    def validate_days(self, days):
        if not days:
            raise serializers.ValidationError('Days should not be empty')

        for day in days:
            pass

        return days

    def validate(self, attrs):
        timezone = attrs.get('timezone')
        current_place = attrs.get('timezone_place')
        timezone_places = VAR_BY_COUNTRY.get(timezone)

        if current_place not in timezone_places.keys():
            raise serializers.ValidationError('selected timezone place does not belong to selected timezone')

        return attrs

    class Meta:
        model = CSchedules
        fields = (
            'id', 'title', 'timezone', 'timezone_name', 'timezone_place',
            'timezone_offset', 'use_work_weekend',
            'use_holiday', 'days'
        )
        read_only_fields = ('id',)

    def create(self, validated_data):
        current_user = self._get_current_user()
        days = validated_data.pop('days', [])

        validated_data['owner'] = current_user if current_user.is_authenticated() else None

        instance = super().create(validated_data)

        self._save_days(instance, days)

        return instance

    def update(self, instance, validated_data):
        days = validated_data.pop('days', [])

        instance = super().update(instance, validated_data)

        self._save_days(instance, days)

        return instance

    def _save_days(self, instance, days):
        # remove old schedule
        instance.days.all().delete()

        # create or update new schedule
        for day_data in days:
            try:
                day = instance.days.get(day_number=day_data['day_number'], end_time=day_data['end_time'])
                self._update_fields(day, day_data)
            except CSchedulesDays.DoesNotExist:
                day = instance.days.create(**day_data)
            day.save()

    def _update_fields(self, instance, data):
        [setattr(instance, k, v) for k, v in data.items()]

    def _get_current_user(self):
        try:
            return self.context['request'].user
        except KeyError:
            return AnonymousUser()
