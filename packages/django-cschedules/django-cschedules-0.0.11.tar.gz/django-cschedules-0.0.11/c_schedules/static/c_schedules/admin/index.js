(function ($) {
    // TODO переделать по django admin

    $.ajaxSetup({
        cache: false
    });

    var $hour_elems = $('.cs-day:not(.cs-day__last)').find('.cs-day__hours').find('.cs-day__hour');
    var $cs_form = $('.cs-form');
    var $nested_forms = $cs_form.find('.nested-forms');
    var $first_nested_day_form = $nested_forms.find('.day-form:first');
    var $timezone_place_select = $('#timezone-place-select');
    var $timezone_place_input = $('#id_timezone_place');
    var $timezone_input = $('#id_timezone');
    var down = false;
    var is_first_active = false;
    var current_form_step = 0;

    function init_events() {
        $hour_elems.mousedown(function () {
            down = true;
            is_first_active = $(this).hasClass('active');
            toggle_elem($(this));
        }).mouseup(function () {
            down = false;
        });

        $hour_elems.mouseenter(function (evt) {
            evt.preventDefault();
            if (down) {
                toggle_elem($(this));
            }
        });

        $timezone_input.on('change', load_timezone_place);

        $('.select-all-row').on('click', function () {

            var id = $(this).attr('id').replace('day-', '');
            var day_sel = '[id^="hour__' + id + '"]';
            var $child_row = $('.cs-day__hour' + day_sel);

            if ($(this).is(":checked")) {
                $child_row.addClass('active');
            } else {
                $child_row.removeClass('active');
            }
        });

        $('.select-all-col').on('click', function () {

            var id = $(this).attr('id').replace('hour-', '');
            var day_sel = '[id$="_' + id + '"]';
            var $child_row = $('.cs-day__hour' + day_sel);

            if ($(this).is(":checked")) {
                $child_row.addClass('active');
            } else {
                $child_row.removeClass('active');
            }
        });

        $('#form-submit').on('click', function (evt) {
            evt.preventDefault();

            save_cshedules();

            // submit after success config data
            $cs_form.submit();
        });
    }

    function save_cshedules() {
        $('.cs-day:not(.cs-day__last)').each(function () {
            var $self = $(this);
            // append timezone place value
            $timezone_place_input.val($timezone_place_select.find('option:selected').text());

            var day_number = $self.attr('id').replace('cs-day-', '');

            var start_hour = null;
            var step_hour = null;
            var step_interval = [];

            var $active_hours = $self.find('.cs-day__hour.active');
            $active_hours.map(function (i, val) {
                var hour = parseInt($(this).attr('id').replace('hour__' + day_number + '_', ''));

                if (step_hour && step_hour + 1 != hour || i + 1 == $active_hours.length) {

                    if ($active_hours.length == i + 1) {
                        step_hour = hour;
                    }

                    var work_time = {
                        'day_number': day_number,
                        'start_time': (start_hour == null ? step_hour : start_hour || '00') + ':00',
                        'end_time': step_hour == 23 ? '23:59' : (step_hour + 1 + ':00')
                    };

                    add_day_form(work_time);

                    start_hour = hour;
                    step_hour = hour;
                    step_interval = [hour];

                } else {

                    step_interval.push(hour);
                    step_hour = hour;

                    if (start_hour == null) {
                        start_hour = hour;
                    }
                }
            });
        });
    }

    function toggle_elem($el) {
        if (is_first_active) {
            $el.removeClass('active');
        } else {
            $el.addClass('active');
        }
    }

    function add_day_form(work_time) {
        // get clone day form
        var $day_form = $first_nested_day_form;
        if (current_form_step) {
            $day_form = $day_form.clone(true, true);
        }

        var form_id_tmp = "days-" + current_form_step;

        // fill day_number
        $day_form.find('input[name$="-day_number"]').attr({
            'id': 'id_' + form_id_tmp + '-day_number',
            'name': form_id_tmp + '-day_number'
        }).val(work_time['day_number']);

        // fill day start time
        $day_form.find('input[name$="-start_time"]').attr({
            'id': 'id_' + form_id_tmp + '-start_time',
            'name': form_id_tmp + '-start_time'
        }).val(work_time['start_time']);

        // fill day end time
        $day_form.find('input[name$="-end_time"]').attr({
            'id': 'id_' + form_id_tmp + '-end_time',
            'name': form_id_tmp + '-end_time'
        }).val(work_time['end_time']);

        // append day form to cs form
        $nested_forms.append($day_form);

        current_form_step += 1;
    }

    function render_if_update() {
        // fill cs area and day form remove

        $nested_forms.find('.day-form').each(function () {
            var start_str_time = $(this).find('input[name$=-start_time]').val();
            var end_str_time = $(this).find('input[name$=-end_time]').val();

            var day_number = $(this).find('input[name$=-day_number]').val();
            var start_time = parseInt(start_str_time.replace(':00', ''));
            var end_time = parseInt(end_str_time.replace(':00', ''));

            if (end_str_time != '23:59:00') {
                end_time -= 1;
            }

            for (var i = start_time; i <= end_time; i++) {
                var hour_id = '#hour__' + day_number + '_' + i;
                $(hour_id).addClass('active');
            }
        });
        // clear all day forms without first (need for clone)
        $nested_forms.find('.day-form:not(:first)').remove();
    }

    function load_timezone_place(evt) {

        var timezone_value = $timezone_input.find('option:selected').attr('value');
        var tz_place_val = $timezone_place_input.val();

        if (timezone_value) {
            $.get('/cshedules/timezone_place/' + timezone_value + '/', function (resp) {
                // clear old results
                $timezone_place_select.empty();

                $.each(resp['results'], function (i, val) {

                    var $opt = $('<option></option>');
                    $opt.attr('value', val);
                    if (val) {
                        $opt.text(val);
                    } else {
                        $opt.text('---------');
                    }

                    if (tz_place_val == val) {
                        $opt.attr('selected', true);
                    }

                    $timezone_place_select.append($opt);
                });
            });
        }
    }

    init_events();
    render_if_update();
    load_timezone_place();
})(django.jQuery);