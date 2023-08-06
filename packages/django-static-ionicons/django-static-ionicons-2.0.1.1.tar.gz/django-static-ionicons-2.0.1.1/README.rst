django-static-ionicons
======================


Django application contain ionicons static files


Install
-------

::

    pip install django-static-ionicons


Settings
--------

::

    INSTALLED_APPS = [
        ...
        "django_static_ionicons",
        ...
    ]


Use static resource
-------------------

::

    {% load staticfiles %}

    {% block style %}
        <link rel="stylesheet" href="{% static "ionicons/css/ionicons.min.css" %}">
    {% endblock %}
