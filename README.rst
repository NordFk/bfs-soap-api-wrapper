BFS SOAP API wrapper
====================

Simply specify the method you are interested in. Currently supporting ``get`` and ``update`` requests.

Instantiate client
------------------

.. code::

    from bfs import Bfs

    config = {
      "bricknode": {
          "wsdl": "https://bfs1.bricknode.com/ENVIRONMENT_NAME/api/bfsapi.asmx?WSDL",
          "credentials": {
            "username": "ENVIRONMENT_USERNAME",
            "password": "ENVIRONMENT_PASSWORD"
          },
          "identifier": "ENVIRONMENT_IDENTIFIER"
        }
    }

    bfs = Bfs(config)



bfs.get
-------
.. code::

    accounts = bfs.get(bfs.methods.GET_ACCOUNTS)


Filter using the ``args`` parameter, support for UUIDs and strings:

.. code::

    instrument = bfs.get(bfs.methods.GET_INSTRUMENTS, args={
        "BrickIds": ["59cc4559-7b6b-490e-816a-89ec12ed8e94"]
    })

    instrument = bfs.get(bfs.methods.GET_INSTRUMENTS, args={
        "ISINs": ["SE0006259594"]
    })

bfs.create
----------
Using the :code:`skip_validation_for_empty_values` flag we can create a minimal object without the client protesting

.. code::

    person = {
        'FirstName': 'Jane',
        'LastName': 'Doe',
        'UserName': 'janedoe',
        'Password': 'janedoe.4.ever',
        'Email': 'jane_doe@mailinator.com',
        'Domain': 'Front',
        'IsNaturalPerson': True
    }

    created_persons = bfs.create(bfs.methods.CREATE_PERSONS, entities=[person], skip_validation_for_empty_values=True)


bfs.update
----------

Unless we are skipping validation, Updating an object often requires
posting an entire object in with valid values, even though you most
likely only want to update a few completely different ones. It is then
mostly helpful to ``get`` the object and then modify it.

Since the results coming back is an ``OrderedDict``, you want to make
it an object before sending it back for updating.

.. code::

    persons = bfs.get(bfs.methods.GET_PERSONS, args={
        "BrickIds": ["6e12ec5a-89e0-4c63-a04c-32141ef90a04"]
    }))

    update_person = bfs.ordered_dict_to_object(persons[0])

You can then update the property you want to change, remember to define
the fields you want affected. Any other fields updated will not be
persisted.

.. code::

    update_person['Email'] = 'john.doe@example.com'

    result = bfs.update(bfs.methods.UPDATE_PERSONS,
                        entities=[update_person],
                        fields={
                            'Email': True
                        })
