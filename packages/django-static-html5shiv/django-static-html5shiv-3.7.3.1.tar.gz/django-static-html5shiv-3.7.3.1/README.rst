django-static-html5shiv
=======================


Django application contain html5shiv static files.


Install
-------

::

    pip install django-static-html5shiv


Settings
--------

::

    INSTALLED_APPS = [
        ...
        "django_static_html5shiv",
        ...
    ]


Use static resource
-------------------

::

    {% load staticfiles %}

    {% block script %}
        <script src="{% static "html5shiv/html5shiv.min.js" %}"></script>
        <script src="{% static "html5shiv/html5shiv-printshiv.min.js" %}"></script>
    {% endblock %}


About package version
---------------------

django-static-html5shiv Uses version number like v3.7.3.1. The first three number is the version number of html5shiv, and the last number is our build number.

