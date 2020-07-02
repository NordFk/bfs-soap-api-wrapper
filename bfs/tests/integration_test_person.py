from unittest import TestCase
import json
import uuid
import random

from bfs import Bfs


class IntegrationTestPerson(TestCase):

    def setUp(self):
        try:
            with open('../../config.json') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print('config.json is not found! Please use the config.template.json and fill in your account details.')

        if "_demo" not in self.config['bricknode']['wsdl']:
            raise Warning('You are running integration tests with a production account')

    def test_create_person_from_dict(self):
        bfs = Bfs(self.config)

        person = {
            'FirstName': f'FirstName {str(uuid.uuid4())}',
            'LastName': f'LastName {str(uuid.uuid4())}',
            'UserName': str(uuid.uuid4()),
            'Password': str(uuid.uuid4()),
            'Email': f'{str(uuid.uuid4())}@mailinator.com',
            'Domain': 'Front',
            'IsNaturalPerson': True
        }

        # Method under test. Using the skip_validation_for_empty_values flag we can create a minimal object to store
        created_persons = bfs.create(bfs.methods.CREATE_PERSONS, entities=[person], skip_validation_for_empty_values=True)

        created_person = created_persons[0]

        # Clean up by removing the new person via the inactivate persons call
        bfs.update(bfs.methods.INACTIVATE_PERSONS, entities=[created_person])

        # Finally let's compare the person that was added
        for key in person.keys():
            self.assertEqual(person[key], created_person[key], f'"{key}" element must match')

    def test_create_person_from_entity(self):
        bfs = Bfs(self.config)

        person = bfs.get_entity(bfs.methods.CREATE_PERSONS, skip_validation_for_empty_values=True)

        # Then some mandatory fields
        person['FirstName'] = f'FirstName {str(uuid.uuid4())}'
        person['LastName'] = f'LastName {str(uuid.uuid4())}'
        person['UserName'] = str(uuid.uuid4())
        person['Password'] = str(uuid.uuid4())
        person['Email'] = f'{str(uuid.uuid4())}@mailinator.com'

        person['Domain'] = 'Front'

        mandatory_bool_props = [
            'IsApproved',
            'IsTaxPayer',
            'IsInsuranceCompany',
            'IsInsuranceProductSupplier',
            'IsApprovedForStructs',
            'IsVerified',
            'IsFundEntity',
            'IsFundCompany',
            'IsIssuer',
            'TRSManualHandling',
            'IsProfessional',
            'MifidOk',
            'IsPEP',
            'IsNaturalPerson'
        ]
        for prop in mandatory_bool_props:
            # An issuer cannot be a natural person
            person[prop] = not person['IsIssuer'] if prop == 'IsNaturalPerson' else bool(random.getrandbits(1))

        # Method under test
        created_persons = bfs.create(bfs.methods.CREATE_PERSONS, entities=[person])

        created_person = created_persons[0]

        # Clean up by removing the new person via the inactivate persons call
        bfs.update(bfs.methods.INACTIVATE_PERSONS, entities=[created_person])

        # Finally let's compare the person that was added
        self.assertEqual(person['FirstName'], created_person['FirstName'], '"FirstName" element must match')
        self.assertEqual(person['LastName'], created_person['LastName'], '"LastName" element must match')
        self.assertEqual(person['UserName'], created_person['UserName'], '"UserName" element must match')
        self.assertEqual(person['Password'], created_person['Password'], '"Password" element must match')
        self.assertEqual(person['Email'], created_person['Email'], '"Email" element must match')
        for prop in mandatory_bool_props:
            self.assertEqual(person[prop], created_person[prop], '"{prop}" element must match')

