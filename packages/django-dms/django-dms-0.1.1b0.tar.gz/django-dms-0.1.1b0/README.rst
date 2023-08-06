django-dms
==========

Description
-----------

django-dms is a Django template filter for displaying decimal degrees
of angles (longitude and latitude) in the Degrees-Minutes-Seconds
notation.

It contains the filters ``longitude`` and ``latitude``. They both take
a number as input and convert it into a DMS value. The filter
``longitude`` accepts any number between -180 and 180, the filter
``latitude`` accepts any number between -90 and 90. If the input value
is not a number or is a number outside the before mentioned ranges
respectively, then the input is displayed without any change and the
filters don't have any effect.

Install
-------

You can install django-dms with ``pip``:

::

    pip install django-dms

Use
---

To use the filters you have to include the app in the ``settings.py`` of
your Django project:

.. code:: python

    INSTALLED_APPS = (
        # other entries
        'django_dms',
    )

In your templates you can use the template filters like this:

::

    {% load dms %}
    {{ 38.8897|latitude }}

The output will be:

::

    38° 53' 23" N
