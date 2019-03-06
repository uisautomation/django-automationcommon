=================
Automation Common
=================

**This repository has moved to https://gitlab.developers.cam.ac.uk/uis/devops/django/automationcommon**

.. image:: https://travis-ci.org/uisautomation/django-automationcommon.svg?branch=master
    :target: https://travis-ci.org/uisautomation/django-automationcommon

.. image:: https://codecov.io/gh/uisautomation/django-automationcommon/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/uisautomation/django-automationcommon


Automation Common is a simple Django app that provides common functionality across different Django projects of the UofC UIS Automation team.

Quick start
-----------

testfixtures

1. Add "automationcommon" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'automationcommon',
    ]

2. Include the automationcommon URLconf in your project urls.py like this::

    url(r'', include('automationcommon.urls')),

3. Run `python manage.py migrate` to create the automationcommon models.

4. All module logging writes to a logger named 'automationcommon'

5. The unittests can be run using the runtests.py script.

6. This module has an audit trail feature that allows you to capture update to / deletes of selected models.
   To track changes to a model simple use the ModelChangeMixin (preceding models.Model).
   To capture the "editor" use automationcommon.models.set_local_user() to set the user to be used in the audit trail
   or configure your app like this::

    MIDDLEWARE_CLASSES = (
        ...
        'automationcommon.middleware.RequestUserMiddleware',
        ...
    )

    If you wish to customise how the mixin decides what to audit you can override your model's
    audit_compare() method (see the method's comment for more details).

