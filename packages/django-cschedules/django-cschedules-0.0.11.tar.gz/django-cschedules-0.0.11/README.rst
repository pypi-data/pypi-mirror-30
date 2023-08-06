=====
CSchedules
=====

Very simple calendar schedule.

Quick start
-----------

1. Add "c_schedules" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.messages',

        'rest_framework', # include if you want use rest api
        'c_schedules',
    ]

if you want use rest_framework, execute pip install djangorestframework

2. Include the c_schedules URLconf in your project urls.py like this::

    url(r'^cschedules/', include('c_schedules.urls')),

3. settings params:
    USE_ONLY_REST_URLS: (default False)
    USE_WITH_REST_URLS: (default False)
    CS_USE_IN_ADMIN_PANEL: (default True)

3. Run `python manage.py migrate` to create the c_schedules models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a c_schedules (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/c_schedules/ to participate in the c_schedules.