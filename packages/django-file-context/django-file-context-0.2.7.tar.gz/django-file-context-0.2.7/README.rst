=============================
Django File Context
=============================

.. image:: https://gitlab.sigmageosistemas.com.br/dev/django-file-context/badges/master/coverage.svg
.. image:: https://gitlab.sigmageosistemas.com.br/dev/django-file-context/badges/master/pipeline.svg
.. image:: https://readthedocs.org/projects/django-file-context/badge/?version=latest

File Context provides an easy way to store different documents/attachments

Documentation
-------------

The full documentation is at https://django-file-context.readthedocs.io.

Quickstart
----------

Install Django File Context::

    pip install django-file-context

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'file_context.apps.FileContextConfig',
        ...
    )

You need to add this to your INSTALLED_APPS, because we have our own
models.

Add Django File Context's URL patterns:

.. code-block:: python

    from file_context import urls as file_context_urls


    urlpatterns = [
        ...
        url(r'^', include(file_context_urls)),
        ...
    ]

This is optional. Actually, you can include your own URLs.

Features
--------

* Generic File model so you can store different kinds of files, images,
etc, using a single model;
* Attach/Detach the file model to other models
* Cool descriptor, so you don't have to keep mangling GenericForeignKeys
inside your models.

Usage
-----

1. First of all, define your first model

:: python
    from file_context.managers import Files
    

    class MyModel(models.Model):

        name = models.CharField(max_length=128)

        files = Files()

2. That's it.
3. You can use the Files API to attach files to MyModel instances, using:

:: python
    
    uploaded_file = File.objects.get(pk=1)
    a = MyModel.objects.create(name='foo')
    a.files.attach(uploaded_file)
    a.files.detach(uploaded_file)
    a.files.clear()

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

* Huge props to django-taggit that inspired me to do the descritor
idea!

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
