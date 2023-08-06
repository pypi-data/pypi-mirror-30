django-static-fontawesome
=========================


Django application contain font-awesome static files


Install
-------

::

    pip install django-static-fontawesome


Settings
--------

::

    INSTALLED_APPS = [
        ...
        "django_static_fontawesome",
        ...
    ]

Use static resource
-------------------

::

    {% load staticfiles %}

    {% block style %}
        <link rel="stylesheet" href="{% static "fontawesome/css/fontawesome-all.min.css" %}">
    {% endblock %}
