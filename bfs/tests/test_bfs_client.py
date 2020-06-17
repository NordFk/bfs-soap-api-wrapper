from unittest import TestCase
import json

from bfs import Bfs


class TestBfs(TestCase):

    def test_bricknode_configuration_warning(self):
        with self.assertRaises(ValueError) as cm:
            bfs = Bfs({})

        self.assertTrue(isinstance(cm.exception, ValueError))
        self.assertEqual(cm.exception.args[0], '"bricknode" element missing from configuration')

    def test_bricknode_configuration_warning(self):
        with self.assertRaises(ValueError) as cm:
            bfs = Bfs({})

        self.assertTrue(isinstance(cm.exception, ValueError))
        self.assertEqual(cm.exception.args[0], '"bricknode" element missing from configuration')

    def test_wsdl_configuration_warning(self):
        with self.assertRaises(ValueError) as cm:
            bfs = Bfs({'bricknode': {}})

        self.assertTrue(isinstance(cm.exception, ValueError))
        self.assertEqual(cm.exception.args[0], '"wsdl" element missing from "bricknode" configuration')

    def test_no_url_in_wsdl_configuration_warning(self):
        with self.assertRaises(ValueError) as cm:
            bfs = Bfs({'bricknode': {'wsdl': ''}})

        self.assertTrue(isinstance(cm.exception, ValueError))
        self.assertEqual(cm.exception.args[0], 'No URL given for the wsdl')
