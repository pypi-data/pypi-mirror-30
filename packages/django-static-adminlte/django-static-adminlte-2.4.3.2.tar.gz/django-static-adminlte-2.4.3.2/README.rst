django-static-adminlte
======================


Django application contain adminlte static files


Install
-------

::

    pip install django-static-adminlte


Settings
--------

::

    INSTALLED_APPS = [
        ...
        "django_static_adminlte",
        ...
    ]

Use static resource
-------------------

::

    {% load staticfiles %}

    {% block style %}
        <link rel="stylesheet" href="{% static "bootstrap/css/bootstrap.min.css" %}">
        <link rel="stylesheet" href="{% static "font-awesome/css/font-awesome.min.css" %}">
        <link rel="stylesheet" href="{% static "ionicons/css/ionicons.min.css" %}">
        <link rel="stylesheet" href="{% static "adminlte/css/AdminLTE.min.css" %}">
        <link rel="stylesheet" href="{% static "adminlte/css/skins/_all-skins.min.css" %}">
        <link rel="stylesheet" href="{% static "adminlte-app-fix.css" %}">
        <!--[if lt IE 9]>
        <script src="{% static "html5shiv/html5shiv.min.js" %}"></script>
        <script src="{% static "respond/respond.min.js" %}"></script>
        <![endif]-->
    {% endblock %}

    {% block script %}
        <script src="{% static "jquery/jquery.min.js" %}"></script>
        <script src="{% static "bootstrap/js/bootstrap.min.js" %}"></script>
        <script src="{% static "jquery-slimscroll/jquery.slimscroll.min.js" %}"></script>
        <script src="{% static "fastclick/fastclick.js" %}"></script>
        <script src="{% static "adminlte/js/adminlte.min.js" %}"></script>
        <script>
            $(document).ready(function () {
                $('.sidebar-menu').tree()
            });
        </script>
    {% endblock %}

