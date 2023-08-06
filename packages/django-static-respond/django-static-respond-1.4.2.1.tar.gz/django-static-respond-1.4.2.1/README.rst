django-static-respond
=====================

Django application contain respond static files.


Install
-------

::

    pip install django-static-respond


Settings
--------

::

    INSTALLED_APPS = [
        ...
        "django_static_respond",
        ...
    ]

Use static resource
-------------------

::

    {% load staticfiles %}

    {% block script %}
        <script src="{% static "respond/respond.min.js" %}"></script>
    {% endblock %}

About the version
-----------------

django-static-respond uses version number like v1.4.2.1. The first three number is the version of the respond static files, and the last number is the build number of this package.

