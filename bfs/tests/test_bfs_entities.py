from unittest import TestCase
import json
import operator
import re

from bfs import Bfs


class TestBfsEntities(TestCase):

    def setUp(self):
        try:
            with open('../../config.json') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print('config.json is not found! Please use the config.template.json and fill in your account details.')

        if "_demo" not in self.config['bricknode']['wsdl']:
            raise Warning('You are running integration tests with a production account')

    def test_get_create_entities(self):
        """
        A test iterating over the services and methods available in the wsdl, trying to instantiate the Create entities
        via the help method bfs.get_entity
        """
        bfs = Bfs(self.config)

        # Let's get the services available
        for service in bfs.client.wsdl.services.values():
            for port in service.ports.values():
                operations = sorted(
                    port.binding._operations.values(),
                    key=operator.attrgetter('name'))

                # Here are the methods
                for operation in operations:
                    method = operation.name
                    if method.startswith('Create'):

                        class_name = Bfs.get_entity_class_name(operation.name)

                        # Method under test
                        entity = bfs.get_entity(class_name)

                        # As our expectations vary a bit due do the inconsistent implementation of the BFS SOAP API,
                        # we mimic the expected outcome here

                        # Only keep "Create" from a select subset of entities
                        expected = re.sub('^%s' % 'Create', '', method) if method not in [
                            'CreateMessages',
                            'CreateNotes',
                            'CreateTasks',
                            'CreateTradingVenues',
                            'CreateWebhookSubscriptions'
                        ] else method

                        # Handle plural forms for most entities
                        if expected not in [
                            'InsurancePolicy',
                            'ManualExecutionInterface',
                            'RecurringOrderTemplatesAutogiro',
                            'File'
                        ]:
                            expected = expected[:-3] + 'y' if expected.endswith('ies') else expected[:-1]

                        # Fix Inconsistent casing and plural form not at end
                        expected = 'RecurringOrderTemplateAutoGiro' \
                            if expected == 'RecurringOrderTemplatesAutogiro' \
                            else expected

                        # Fix completely different entity type than method name "CreateFile"
                        expected = 'FileInfoUpload' if expected == 'File' else expected
                        expected = 'SuperTransaction' if expected == 'BusinessTransaction' else expected

                        self.assertEqual(expected, entity.__class__.__name__)

    def test_get_update_entities(self):
        """
        A test iterating over the services and methods available in the wsdl, trying to instantiate the Update entities
        via the help method bfs.get_entity
        """
        bfs = Bfs(self.config)

        # Let's get the services available
        for service in bfs.client.wsdl.services.values():
            for port in service.ports.values():
                operations = sorted(
                    port.binding._operations.values(),
                    key=operator.attrgetter('name'))

                # Here are the methods
                for operation in operations:
                    method = operation.name
                    if method.startswith('Update'):

                        class_name = Bfs.get_entity_class_name(operation.name)

                        # Method under test
                        entity = bfs.get_entity(class_name)

                        # As our expectations vary a bit due do the inconsistent implementation of the BFS SOAP API,
                        # we mimic the expected outcome here

                        # Remove "Update" from a select subset of entities
                        expected = re.sub('^%s' % 'Update', '', method) if method in [
                            'UpdateAllocationProfiles'
                        ] else method

                        # Handle plural forms for most entities
                        if expected not in [
                            'UpdateRecurringOrderTemplateAutoGiro',
                            'UpdateWhiteLabel'
                        ]:
                            expected = expected[:-3] + 'y' if expected.endswith('ies') else expected[:-1]

                        # Fix Casing anomalies
                        expected = 'UpdateFundCompany' if expected == 'UpdateFundcompany' else expected
                        expected = 'UpdateFundEntity' if expected == 'UpdateFundentity' else expected

                        self.assertEqual(expected, entity.__class__.__name__)

    def test_get_derived_entities(self):
        """
        A test getting a derived entity type based on the content of the entity
        """
        bfs = Bfs(self.config)

        class_name = 'CurrencyExchangeOrder'

        # Method under test
        entity = bfs.get_entity(class_name, {
            'BuyAmount': 0
        })
        self.assertEqual('CurrencyExchangeOrderBuy', entity.__class__.__name__)

        # Method under test
        entity = bfs.get_entity(class_name, {
            'SellAmount': 0
        })
        self.assertEqual('CurrencyExchangeOrderSell', entity.__class__.__name__)
