=================
Automation Common
=================

Automation Common is a simple Django app that provides common functionality across different Django projects of the UofC UIS Automation team.

Quick start
-----------

1. Add "automationcommon" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'automationcommon',
    ]

2. Include the automationcommon URLconf in your project urls.py like this::

    url(r'', include('automationcommon.urls')),

3. Run `python manage.py migrate` to create the automationcommon models.

