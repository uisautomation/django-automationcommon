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

4. All module logging writes to a logger named 'automationcommon'

5. This module has an audit trail feature that allows you to capture update to / deletes of selected models.
   To track changes to a model simple use the ModelChangeMixin.
   To capture the "editor" use automationcommon.models.set_local_user() to set the user to be used in the audit trail
   or configure your app like this::

    MIDDLEWARE_CLASSES = (
        ...
        'automationcommon.middleware.RequestUserMiddleware',
    )
