django-static-jquery3
=====================


Django application contain jquery static files


Install
-------

::

    pip install django-static-jquery3


Settings
--------

::

    INSTALLED_APPS = [
        ...
        "django_static_jquery3",
        ...
    ]

Use static resource
-------------------

::

    {% load staticfiles %}

    {% block script %}
        <script src="{% static "jquery3/jquery.js" %}"></script>
        <script src="{% static "jquery3/jquery.min.js" %}"></script>
        <script src="{% static "jquery3/jquery.min.map" %}"></script>
        <script src="{% static "jquery3/jquery.slim.js" %}"></script>
        <script src="{% static "jquery3/jquery.slim.min.js" %}"></script>
        <script src="{% static "jquery3/jquery.slim.min.map" %}"></script>
    {% endblock %}
