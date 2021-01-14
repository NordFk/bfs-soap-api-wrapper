BFS SOAP API wrapper
====================

Simply specify the method you are interested in.

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


bfs.execute
-----------
The :code:`execute` method is added for code clarity, it has the same internal requirements as :code:`create`

.. code::

    transfer_orders = [{
            'FromAccountBrickId': 'fbce4894-5f3c-49c3-87c4-62e8f3dae52f',
            'ToAccountBrickId': 'ef403f20-dfa7-4930-9e65-409d744856f8',
            'Units': 607500,
            'Comment': 'My comment',
            'TradeDate': 2021-01-11,
            'SettlementDate': 2021-01-13,
            'ValueDate': 2021-01-11,
            'InstrumentBrickId': '142f5c35-26b3-4697-87ac-81e672280b17',
            'OverrideOwnershipChangeValidation': True
        }]

    created_transfer_orders = bfs.create(bfs.methods.CREATE_INTERNAL_INSTRUMENT_TRANSFER_ORDERS, entities=transfer_orders,
                                 skip_validation_for_empty_values=True)

    entities = list(map(lambda o: {'InternalTransferOrderBrickId': o['BrickId']}, created_transfer_orders))
    result = bfs.execute(bfs.methods.EXECUTE_INTERNAL_TRANSFER_ORDERS, entities=entities)


bfs.update
----------

Unless we are skipping validation, Updating an object often requires
posting an entire object in with valid values, even though you most
likely only want to update a few completely different ones. It is then
mostly helpful to ``get`` the object and then modify it.


.. code::

    persons = bfs.get(bfs.methods.GET_PERSONS, args={
        'BrickIds': ['6e12ec5a-89e0-4c63-a04c-32141ef90a04']
    }))

    update_person = persons[0]

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

bfs.delete
----------

This can be used for deleting POAs and Allocation Profiles. Not supporting DeleteFile, which requires a FileInfoDelete
object as input.

.. code::

    brick_ids = [
        '3038fc58-731b-47c4-ae55-0aada120e200',
        'a018c8f1-f3f1-4ac5-b392-a33e2167a17e'
    ]

    result = bfs.delete(bfs.methods.DELETE_POAS, brick_ids=brick_ids)