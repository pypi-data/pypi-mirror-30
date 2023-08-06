API Star CRUD
=============

:Version: 0.1.0
:Status: Production/Stable
:Author: José Antonio Perdiguero López

API Star tools to create CRUD resources.

Features
--------
The resources are classes with a default implementation for **methods**:

* `create`: Create a new element for this resource.
* `retrieve`: Retrieve an element of this resource.
* `update`: Update (partially or fully) an element of this resource.
* `delete`: Delete an element of this resource.
* `list`: List resource collection.
* `replace`: Replace resource collection with a new one.
* `drop`: Drop resource collection.

----

The **routes** for these methods are:

========== ======== ================
Method     Verb     URL
========== ======== ================
`create`   `POST`   `/`
`retrieve` `GET`    `/{element_id}/`
`update`   `PUT`    `/{element_id}/`
`delete`   `DELETE` `/{element_id}/`
`list`     `GET`    `/`
`replace`  `PUT`    `/`
`drop`     `DELETE` `/`
========== ======== ================

Quick start
-----------
Install API star CRUD:

.. code:: bash

    pip install apistar-crud

Create a *model* for your resource:

.. code:: python

    # Example using SQL Alchemy

    class PuppyModel(Base):
        __tablename__ = "Puppy"

        id = Column(Integer, primary_key=True)
        name = Column(String)

Create a *type* for your resource:

.. code:: python

    class PuppyType(typesystem.Object):
        properties = {
            'id': typesystem.Integer,
            'name': typesystem.String
        }

Now create your resource:

.. code:: python

    from apistar_crud.sqlalchemy import Resource

    class PuppyResource(metaclass=Resource):
        model = PuppyModel
        type = PuppyType
        methods = ('create', 'retrieve', 'update', 'delete', 'list', 'replace', 'drop')

The resource generates his own routes, so you can add it to your main *routes.py*:

.. code:: python

    from apistar import Include

    routes = [
        Include('/puppy/', PuppyResource.routes, namespace='puppy'),
    ]
