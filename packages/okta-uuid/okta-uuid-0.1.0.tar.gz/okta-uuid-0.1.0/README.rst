`okta-uuid`
===========

This is a simple module for turning Okta's user IDs (which *appear* to be
base62-encoded integers) into UUIDs, and vice versa. This is useful for
integrating Okta with systems or services where you don't necessarily want to
use string identifiers.

Installing
----------

First, make sure you're using Python 3.2 or newer.

Install from pypi: ``pip install okta-uuid``


Developing
----------

* Create a virtualenv.
* Clone this repo.
* Install the requirements: ``python setup.py develop``.
* Hack away!

There's a (small!) test suite included. You can run it with ``python test.py``.


Using
-----

Get a UUID from an Okta ID:

.. code-block:: python

    idstr = '00ABCD1234wxyz5678pq'
    oid = okta_uuid.OktaUserId(idstr)

    print(repr(oid))
    print(oid)
    print(oid.uuid)

    # output:
    #
    # OktaUserId('00ABCD1234wxyz5678pq')
    # 00ABCD1234wxyz5678pq
    # cb406d76-d66a-6007-5001-36cc7b010000

Get an Okta ID from a UUID:

.. code-block:: python

    idstr = '00ABCD1234wxyz5678pq'
    oid = okta_uuid.OktaUserId(idstr)
    new_oid = okta_uuid.OktaUserId.from_uuid(oid.uuid)

    print(new_oid)
    print(oid == new_oid)

    # output:
    #
    # 00ABCD1234wxyz5678pq
    # True
