=============================
Django Chaos
=============================

.. image:: https://gitlab.sigmageosistemas.com.br/dev/django-chaos/badges/master/coverage.svg
.. image:: https://gitlab.sigmageosistemas.com.br/dev/django-chaos/badges/master/pipeline.svg
.. image:: https://readthedocs.org/projects/django-chaos/badge/?version=latest
Project to do project management with a gantt chart.

Documentation
-------------

The full documentation is at https://django-chaos.readthedocs.io.

Quickstart
----------

Install Django Chaos::

    pip install django-chaos

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'chaos.apps.ChaosConfig',
        ...
    )

Add Django Chaos's URL patterns:

.. code-block:: python

    from chaos import urls as chaos_urls


    urlpatterns = [
        ...
        url(r'^', include(chaos_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage




History
-------

0.1.0 (2017-10-09)
++++++++++++++++++

* First release on PyPI.


