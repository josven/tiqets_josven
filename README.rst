tiqets assignment
=================

I opted for not using any frameworks, and solving the assignment by only using Python standard libs, since using something like Django would add a lot of overhead and it was not required in the assignment.
But if this be an application I would use a framework and would probably do the following:

Django, have all batteries included. I could easily use the Django model framework to define the 3 models.
Also, make use of the Django field and model validation to avoid bad data being ingested. Django's ORM
makes it easy to create aggregations and annotations to retrieve top consumers and find unused bar codes.

To load in the data I would probably use something like a django-app like django-csvimport.

If I were to go the FastAPI route I would probably use the sqlmodel package that both leverages Pydantic and SQLAlchemy. Pydantic also has methods to validate fields and models.

Usage
-----
Run with docker, in Dockerfile directory:

    $ docker build -t tiq .

    $ docker run -t tiq:latest


Or run with python 3.12 interpreter

    $ python .\tiqets\assignment.py


To run the tests and all checks with docker, in Dockerfile directory

    $ docker run -t tiq:latest tox

To run the tests and all the checks with python 3.12 interpreter, in tox.ini directory

    $ tox

Requirements
^^^^^^^^^^^^
- docker

or

- python 3.12
- tox


Schema
------

Simple schema on how this can be stored in a rel DB.

.. raw:: html
  :file: schema.svg


.. code-block:: rst

    // Docs: https://dbml.dbdiagram.io/docs

    Table Customers {
      id integer [primary key]
    }

    Table Orders {
      id integer [primary key]
      customer_id integer [ref: > Customers.id]
    }

    Table Tickets {
      id integer [primary key]
      ean varchar [unique, not null]
      order_id integer [ref: > Orders.id]
    }


Licence
-------
MIT

Authors
-------

`tiqets` was written by `Jonas Svensson <jonas.s.svensson@gmail.com>`_.
