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

    def test_create_entities(self):
        bfs = Bfs(self.config)

        for service in bfs.client.wsdl.services.values():
            for port in service.ports.values():
                operations = sorted(
                    port.binding._operations.values(),
                    key=operator.attrgetter('name'))

                for operation in operations:
                    method = operation.name
                    if method.startswith('Create'):

                        entity = bfs.get_entity(operation.name)

                        # Only keep "Create" from a select subset of entities
                        class_name = re.sub('^%s' % 'Create', '', method) if method not in [
                            'CreateMessages',
                            'CreateNotes',
                            'CreateTasks'
                        ] else method

                        expected = class_name

                        # Handle plural forms (if needed)
                        if expected not in [
                            'InsurancePolicy',
                            'ManualExecutionInterface',
                            'RecurringOrderTemplatesAutogiro',
                            'File'
                        ]:
                            expected = class_name[:-3] + 'y' if class_name.endswith('ies') else class_name[:-1]

                        # Fix Inconsistent casing and plural form not at end
                        expected = 'RecurringOrderTemplateAutoGiro' if expected == 'RecurringOrderTemplatesAutogiro' else expected

                        # Fix completely different entity type than method name "CreateFile"
                        expected = 'FileInfoUpload' if expected == 'File' else expected

                        self.assertEqual(expected, entity.__class__.__name__)

    def test_update_entities(self):
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
                        entity = bfs.get_entity(method)

                        # Remove "Update" from a select subset of entities
                        class_name = re.sub('^%s' % 'Update', '', method) if method in [
                            'UpdateAllocationProfiles'
                        ] else method

                        expected = class_name

                        # Handle plural forms (if needed)
                        if expected not in [
                            'UpdateRecurringOrderTemplateAutoGiro',
                            'UpdateWhiteLabel'
                        ]:
                            expected = class_name[:-3] + 'y' if class_name.endswith('ies') else class_name[:-1]

                        # Fix Casing anomalies
                        expected = 'UpdateFundCompany' if expected == 'UpdateFundcompany' else expected
                        expected = 'UpdateFundEntity' if expected == 'UpdateFundentity' else expected

                        self.assertEqual(expected, entity.__class__.__name__)

