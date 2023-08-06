django-static-echarts
=====================


Django application contain echarts static files


Install
-------

::

    pip install django-static-echarts


Settings
--------

::

    INSTALLED_APPS = [
        ...
        "django_static_echarts",
        ...
    ]

Use static resource
-------------------

::

    {% load staticfiles %}

    {% block script %}
        <script src="{% static "echarts/echarts.min.js" %}"></script>
        <script src="{% static "echarts/theme/vintage.js" %}"></script>
        <script src="{% static "echarts/map/js/china.js" %}"></script>
    {% endblock %}
