.. This file is a part of the AnyBlok Marshmallow project
..
..    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

.. image:: https://travis-ci.org/AnyBlok/AnyBlok_Marshmallow.svg?branch=master
    :target: https://travis-ci.org/AnyBlok/AnyBlok_Marshmallow
    :alt: Build status

.. image:: https://coveralls.io/repos/github/AnyBlok/AnyBlok_Marshmallow/badge.svg?branch=master
    :target: https://coveralls.io/github/AnyBlok/AnyBlok_Marshmallow?branch=master
    :alt: Coverage

.. image:: https://img.shields.io/pypi/v/AnyBlok_Marshmallow.svg
   :target: https://pypi.python.org/pypi/AnyBlok_Marshmallow/
   :alt: Version status

.. image:: https://readthedocs.org/projects/anyblok-marshmallow/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://doc.anyblok-marshmallow.anyblok.org/?badge=latest


AnyBlok Marshmallow
===================

Improve AnyBlok `AnyBlok <http://doc.anyblok.org>`_ to add validator, serializer and 
deserializer schema with `marshmallow <https://marshmallow.readthedocs.io/en/latest/>`_.

This module is a wrapper of `marshmallow-sqlalchemy <https://marshmallow-sqlalchemy.readthedocs.io/en/latest/>`_,
the goal is to give the SQLAlchemy Model build by AnyBlok to this librairy

AnyBlok Marshmallow is released under the terms of the `Mozilla Public License`.

See the `latest documentation <http://doc.anyblok-marshmallow.anyblok.org/>`_


.. This file is a part of the AnyBlok / Marshmallow project
..
..    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

.. contents::

Front Matter
============

Information about the AnyBlok / Marshmallow project.

Project Homepage
----------------

AnyBlok is hosted on `github <http://github.com>`_ - the main project
page is at https://github.com/AnyBlok/AnyBlok_Marshmallow. Source code is
tracked here using `GIT <https://git-scm.com>`_.

Releases and project status are available on Pypi at
http://pypi.python.org/pypi/anyblok_marshmallow.

The most recent published version of this documentation should be at
http://doc.anyblok-marshmallow.anyblok.org.

Project Status
--------------

AnyBlok with Marshmallow is currently in beta status and is expected to be fairly
stable.   Users should take care to report bugs and missing features on an as-needed
basis.  It should be expected that the development version may be required
for proper implementation of recently repaired issues in between releases;

Installation
------------

Install released versions of AnyBlok from the Python package index with
`pip <http://pypi.python.org/pypi/pip>`_ or a similar tool::

    pip install anyblok_marshmallow

Installation via source distribution is via the ``setup.py`` script::

    python setup.py install

Installation will add the ``anyblok`` commands to the environment.

Unit Test
---------

Run the test with ``nose``::

    pip install nose
    nosetests anyblok_marshmallow/tests

Dependencies
------------

AnyBlok works with **Python 3.3** and later. The install process will
ensure that `AnyBlok <http://doc.anyblok.org>`_,
`marshmallow <https://marshmallow.readthedocs.io/en/latest/>`_ and 
`marshmallow-sqlalchemy <https://marshmallow-sqlalchemy.readthedocs.io/en/latest/>`_ 
are installed, in addition to other dependencies. 
The latest version of them is strongly recommended.


Contributing (hackers needed!)
------------------------------

Anyblok / Marshmallow is at a very early stage, feel free to fork, talk with core
dev, and spread the word!

Author
------

Jean-Sébastien Suzanne

Contributors
------------

`Anybox <http://anybox.fr>`_ team:

* Jean-Sébastien Suzanne

`Sensee <http://sensee.com>`_ team:

* Franck Bret

Bugs
----

Bugs and feature enhancements to AnyBlok should be reported on the `Issue
tracker <https://github.com/AnyBlok/AnyBlok_Marshmallow/issues>`_.

.. This file is a part of the AnyBlok / Marshmallow project
..
..    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

.. contents::

Memento
=======

Declare your **AnyBlok model**
------------------------------

::

    from anyblok.column import Integer, String
    from anyblok.relationship import Many2One, Many2Many
    from anyblok import Declarations


    @Declarations.register(Declarations.Model)
    class City:

        id = Integer(primary_key=True)
        name = String(nullable=False)
        zipcode = String(nullable=False)

        def __repr__(self):
            return '<City(name={self.name!r})>'.format(self=self)


    @Declarations.register(Declarations.Model)
    class Tag:

        id = Integer(primary_key=True)
        name = String(nullable=False)

        def __repr__(self):
            return '<Tag(name={self.name!r})>'.format(self=self)


    @Declarations.register(Declarations.Model)
    class Customer:
        id = Integer(primary_key=True)
        name = String(nullable=False)
        tags = Many2Many(model=Declarations.Model.Tag)

        def __repr__(self):
            return '<Customer(name={self.name!r}, '
                   'tags={self.tags!r})>'.format(self=self)


    @Declarations.register(Declarations.Model)
    class Address:

        id = Integer(primary_key=True)
        street = String(nullable=False)
        city = Many2One(model=Declarations.Model.City, nullable=False)
        customer = Many2One(
            model=Declarations.Model.Customer, nullable=False,
            one2many="addresses")


.. warning::

    The **AnyBlok model** must be declared in a blok


Declare your schema
-------------------

::

    from anyblok_marshmallow import ModelSchema, PostLoadSchema, Nested

    class CitySchema(ModelSchema):

        class Meta:
            model = 'Model.City'


    class TagSchema(ModelSchema):

        class Meta:
            model = 'Model.Tag'


    class AddressSchema(ModelSchema):

        # follow the relationship Many2One and One2One
        city = Nested(CitySchema)

        class Meta:
            model = 'Model.Address'


    class CustomerSchema(PostLoadSchema, ModelSchema):

        # follow the relationship One2Many and Many2Many
        # - the many=True is required because it is *2Many
        # - exclude is used to forbid the recurse loop
        addresses = Nested(AddressSchema, many=True, exclude=('customer', ))
        tags = Nested(TagSchema, many=True)

        class Meta:
            model = 'Model.Customer'
            # optionally attach an AnyBlok registry
            # to use for serialization, desarialization and validation
            registry = registry


    customer_schema = CustomerSchema()


.. note::

    **New** in version **1.1.0** the Nested field must come from **anyblok_marshmallow**,
    because **marshmallow** cache the Nested field with the context. And the context is not propagated
    again if it changed

.. note::

    **Ref** in version **1.4.0**, ``post_load_return_instance`` was replaced by the mixin class
    ``PostLoadSchema``


(De)serialize your data and validate it
---------------------------------------

::

    customer = registry.Customer.insert(name="JS Suzanne")
    tag1 = registry.Tag.insert(name="tag 1")
    customer.tags.append(tag1)
    tag2 = registry.Tag.insert(name="tag 2")
    customer.tags.append(tag2)
    rouen = registry.City.insert(name="Rouen", zipcode="76000")
    paris = registry.City.insert(name="Paris", zipcode="75000")
    registry.Address.insert(customer=customer, street="Somewhere", city=rouen)
    registry.Address.insert(customer=customer, street="Another place", city=paris)

    dump_data = customer_schema.dump(customer).data
    # {
    #     'id': 1,
    #     'name': 'JS Suzanne',
    #     'tags': [
    #         {
    #             'id': 1,
    #             'name': 'tag 1',
    #         },
    #         {
    #             'id': 2,
    #             'name': 'tag 2',
    #         },
    #     ],
    #     'addresses': [
    #         {
    #             'id': 1
    #             'street': 'Somewhere'
    #             'city': {
    #                 'id': 1,
    #                 'name': 'Rouen',
    #                 'zipcode': '76000',
    #             },
    #         },
    #         {
    #             'id': 2
    #             'street': 'Another place'
    #             'city': {
    #                 'id': 2,
    #                 'name': 'Paris',
    #                 'zipcode': '75000',
    #             },
    #         },
    #     ],
    # }

    customer_schema.load(dump_data).data
    # <Customer(name='JS Suzanne' tags=[<Tag(name='tag 1')>, <Tag (name='tag 2')>])>

    errors = customer_schema.validate(dump_data)
    # dict with all the validating errors

.. note::

    We have an instance of the model cause of the mixin ``PostLoadSchema``


Give the registry
-----------------

The schema need to have the registry.

If no registry found when the de(serialization) or validation then the 
**RegistryNotFound** exception will be raised.

Add the **registry** by the Meta
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the solution given in the main exemple::

    class CustomerSchema(ModelSchema):

        class Meta:
            model = 'Model.Customer'
            registry = registry


Add the **registry** during init
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This solution is use during the instanciation

::

    customer_schema = CustomerSchema(registry=registry)


Add the **registry** by the context
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This solution is use during the instanciation or after

::

    customer_schema = CustomerSchema(context={'registry': registry})

or

::

    customer_schema = CustomerSchema()
    customer_schema.context['registry'] = registry


Add the **registry** when the de(serialization or validatoris called
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    customer_schema.dump(customer, registry=registry)
    customer_schema.load(dump_data, registry=registry)
    customer_schema.validate(dump_data, registry=registry)


**model** option
----------------

This option add in the model name. As the registry, this option
can be passed by definition, initialization, context or during the call of the (de)serialization / validation

::

    class AnySchema(ModelSchema):

        class Meta:
            model = "Model.Customer"

or

::

    any_schema = AnySchema(model="Model.customer")

or

::

    any_schema.context['model'] = "Model.Customer"

or

::

    any_schema.dump(instance, model="Model.Customer")
    any_schema.load(dump_data, model="Model.Customer")
    any_schema.validate(dump_data, model="Model.Customer")


**only_primary_key** option
---------------------------

This option add in the only argument the primary keys of the model. As the registry, this option
can be passed by definition, initialization, context or during the call of the (de)serialization / validation

::

    class CustomerSchema(ModelSchema):

        class Meta:
            model = "Model.Customer"
            only_primary_key = True

or

::

    customer_schema = CustomerSchema(only_primary_key=True)

or

::

    customer_schema.context['only_primary_key'] = True

or

::

    customer_schema.dump(instance, only_primary_key=True)
    customer_schema.load(dump_data, only_primary_key=True)
    customer_schema.validate(dump_data, only_primary_key=True)

.. This file is a part of the AnyBlok / Marshmallow project
..
..    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
..    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

.. contents::

CHANGELOG
=========

1.4.0 (2018-04-07)
------------------

* Replace **post_load_return_instance** method by **PostLoadSchema** class
* In the case of the field **Selection**, the validator **OneOf** is 
  applied with the available values come from the AnyBlok columns
* Replace **marshmallow_sqlalchemy.fields.Related** by 
  **anyblok_marshmallow.fields.Nested**. The goal is to improve the consistent 
  between all field in the schema

1.3.0 (2017-12-23)
------------------

* [ADD] unittest on some case
* [FIX] AnyBlok field.Function is return as MarshMallow fields.Raw
* [ADD] fields.File, type to encode and decode to/from base 64

1.2.0 (2017-11-30)
------------------

* [REF] decrease complexity
* [IMP] Add ``validates_schema`` on ModelSchema to automaticly check
  if the field exist on the model

1.1.0 (2017-11-02)
------------------

* Add option put only the primary keys
* Fix the Front page
* REF model option, can be given by another way than Meta
* Put RegistryNotFound in exceptions
* Add Nested field, this field is not and have not to be cached

1.0.2 (2017-10-25)
------------------

* Fix pypi documentation

1.0.0 (2017-10-24)
------------------

* Add marshmallow schema for AnyBlok for:

  - Serialization
  - Deserialization
  - Validation


