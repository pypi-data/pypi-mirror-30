django-static-bootstrap
=======================


Django application contain bootstrap static files.


Install
-------

::

    pip install django-static-bootstrap


Settings
--------

::

    INSTALLED_APPS = [
        ...
        "django_static_bootstrap",
        ...
    ]


Use static resource
-------------------

::

    {% load staticfiles %}

    {% block style %}
        <link rel="stylesheet" href="{% static "bootstrap/css/bootstrap.min.css" %}">
        <link rel="stylesheet" href="{% static "bootstrap/css/bootstrap-theme.min.css" %}">
    {% endblock %}

    {% block script %}
        <script src="{% static "bootstrap/js/bootstrap.min.js" %}"></script>
    {% endblock %}
