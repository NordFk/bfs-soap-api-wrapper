from collections import OrderedDict

from zeep import Client
from zeep import xsd
import zeep.helpers
import zeep.exceptions
import logging.config
import re
from .constants import methods


class Bfs:
    client = None
    factory = None
    credentials = None
    identifier = None
    methods = methods

    def __init__(self, config, verbose: bool = False):
        self.__init_logging(verbose)
        self.__init_client(config)

    @staticmethod
    def __init_logging(self, verbose: bool = False):
        if verbose:
            logging.config.dictConfig({
                'version': 1,
                'formatters': {
                    'verbose': {
                        'format': '%(name)s: %(message)s'
                    }
                },
                'handlers': {
                    'console': {
                        'level': 'DEBUG',
                        'class': 'logging.StreamHandler',
                        'formatter': 'verbose',
                    },
                },
                'loggers': {
                    'zeep.transports': {
                        'level': 'DEBUG',
                        'propagate': True,
                        'handlers': ['console'],
                    },
                }
            })
        else:
            logging.getLogger('zeep').setLevel(logging.ERROR)

    def __init_client(self, config: dict):
        if self.client is None:
            if not 'bricknode' in config:
                raise ValueError('"bricknode" element missing from configuration')
            if not 'wsdl' in config['bricknode']:
                raise ValueError('"wsdl" element missing from "bricknode" configuration')
            self.client = Client(config['bricknode']['wsdl'])
            self.factory = self.client.type_factory('ns0')
            self.credentials = self.factory.Credentials(UserName=config['bricknode']['credentials']['username'],
                                                        Password=config['bricknode']['credentials']['password'])
            self.identifier = config['bricknode']['identifier']

    def get_fields(self, method: str, default_value: bool = True):
        """
        Gets fields object based on results object. Mitigates the plural form inconsistency present in the API
        :param method:
        :param default_value:
        :return:
        """
        try:
            fields_method = getattr(self.factory, method + 'Fields')
        except zeep.exceptions.LookupError:
            fields_method = getattr(self.factory, method[:-1] + 'Fields')

        fields = fields_method()
        for key in fields:
            fields[key] = default_value
        return fields

    def get_args(self, method: str):
        """
        Gets args object based on results object. Mitigates the plural form inconsistency present in the API
        :param method:
        :return:
        """
        try:
            args_method = getattr(self.factory, method + 'Args')
        except zeep.exceptions.LookupError:
            args_method = getattr(self.factory, method[:-1] + 'Args')
        return args_method()

    @staticmethod
    def __get_entity_class_name(method: str):
        """
        This method aligns the expected object names with the method that will use it. Eg. CreateAccount uses Account as
        object, while the UpdateAccount method uses UpdateAccount objects and arrays thereof.
        CreateMessage, on the other hand, uses CreateMessage as object.
        :param method:
        :return:
        """
        # "Create" entities are not prefixed with "Create". Unless, of course, it is CreateMessage, CreateNote, or
        # CreateTask
        method = re.sub('^%s' % 'Create', '', method) if method not in [
            'CreateMessages',
            'CreateNotes',
            'CreateTasks'
        ] else method

        # "Update" entities are always prefix with "Update". Unless, of course, it is UpdateAllocationProfiles
        method = re.sub('^%s' % 'Update', '', method) if method in [
            'UpdateAllocationProfiles'
        ] else method

        # Casing anomalies
        method = 'UpdateFundCompanies' if method == 'UpdateFundcompanies' else method
        method = 'UpdateFundEntities' if method == 'UpdateFundentities' else method

        # Inconsistent casing and plural form not at end
        method = 'RecurringOrderTemplateAutoGiro' if method == 'RecurringOrderTemplatesAutogiro' else method

        # Completely different entity type
        method = 'FileInfoUpload' if method == 'File' else method

        return method

    def get_entity(self, method: str, entity: dict = None, skip_validation_for_empty_values: bool = False):
        """
        Gets entity object based on method
        :param method: The method used to determine what type to use
        :param entity: Optional entity object to convert
        :param skip_validation_for_empty_values: Set this to True to ignore validation that required values are set
        :return:
        """
        class_name = self.__get_entity_class_name(method)
        try:
            entity_method = getattr(self.factory, class_name)
        except zeep.exceptions.LookupError:
            try:
                entity_method = getattr(self.factory, class_name[:-1])
            except zeep.exceptions.LookupError:
                entity_method = getattr(self.factory, class_name[:-3] + "y")

        _entity = entity_method()
        if skip_validation_for_empty_values:
            for key in [a for a in dir(_entity) if not a.startswith('__')]:
                _entity[key] = xsd.SkipValue

        if type(entity) is dict:
            for key in entity.keys():
                _entity[key] = entity[key]

        return _entity

    def get_entity_array(self, method: str, entities: list):
        """
        Gets an entity array based on method
        :param method:
        :param entities:
        :return:
        """
        class_name = self.__get_entity_class_name(method)
        try:
            entity_array_method = getattr(self.factory, "ArrayOf" + class_name)
        except zeep.exceptions.LookupError:
            entity_array_method = getattr(self.factory, "ArrayOf" + class_name[:-1])
        return entity_array_method(entities)

    def __argument_transform(self, value):
        """
        Transforms the argument to suit the soap client
        :param value:
        :return:
        """
        p = re.compile('^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')
        if isinstance(value, list) and len(value) > 0:
            if p.match(value[0]):
                return self.factory.ArrayOfGuid(value)
            else:
                return self.factory.ArrayOfString(value)
        return value

    def get(self, method: str, args: dict = None, fields: dict = None, raw_result: bool = False):
        """
        Makes a call to the API, preparing the request and default fields (true) and adds+transforms the arguments
        :param method: The Bricknode API method name
        :param args: Any arguments you would like to pass (optional)
        :param fields: Any field settings you would like to pass (optional)
        :param raw_result: Set to True to get the raw result back (optional)
        :return:
        """
        _fields = self.get_fields(method)
        if type(fields) is dict:
            for key in fields.keys():
                _fields[key] = fields[key]

        _args = self.get_args(method)
        if type(args) is dict:
            for key in args.keys():
                _args[key] = self.__argument_transform(args[key])

        query_method = getattr(self.client.service, method)

        result = query_method({
            'Credentials': self.credentials,
            'identify': self.identifier,
            'Args': _args,
            'Fields': _fields
        })

        return result if raw_result else self.get_response_rows(zeep.helpers.serialize_object(result), method)

    def create(self, method: str, entities: list = None, skip_validation_for_empty_values: bool = False,
               raw_result=False):
        """
        Makes a call to the API, preparing the request and default fields (true) and adds+transforms the arguments
        :param method: The Bricknode API method name
        :param entities: The entities we want to create
        :param skip_validation_for_empty_values: Set this to True to ignore validation that required values are set
        :param raw_result: Set to True to get the raw result back (optional)
        :return:
        """

        _entities = []
        for entity in entities:
            _entities.append(entity if type(entity) != dict
                             else self.get_entity(method, entity, skip_validation_for_empty_values))

        query_method = getattr(self.client.service, method)

        result = query_method({
            'Credentials': self.credentials,
            'identify': self.identifier,
            'Entities': self.get_entity_array(method, _entities)
        })

        return result if raw_result else self.get_response_rows(zeep.helpers.serialize_object(result), method)

    def update(self, method: str, entities: list = None, fields: dict = None,
               skip_validation_for_empty_values: bool = False, raw_result=False):
        """
        Makes a call to the API, preparing the request and default fields (true) and adds+transforms the arguments
        :param method: The Bricknode API method name
        :param entities: The entities we want to update
        :param fields: Any field settings you would like to pass (optional)
        :param skip_validation_for_empty_values: Set this to True to ignore validation that required values are set
        :param raw_result: Set to True to get the raw result back (optional)
        :return:
        """
        _fields = self.get_fields(method, False)

        if type(fields) is dict:
            for key in fields.keys():
                _fields[key] = fields[key]

        _entities = []
        for entity in entities:
            _entities.append(entity if type(entity) != dict
                             else self.get_entity(method, entity, skip_validation_for_empty_values))

        query_method = getattr(self.client.service, method)

        result = query_method({
            'Credentials': self.credentials,
            'identify': self.identifier,
            'Entities': self.get_entity_array(method, _entities),
            'Fields': _fields
        })

        return result if raw_result else self.get_response_rows(zeep.helpers.serialize_object(result), method)

    def delete(self, method: str, brick_ids: list = None):
        """
        Makes a call to the API, preparing the request and default fields (true) and adds+transforms the arguments
        :param method: The Bricknode API method name
        :param brick_ids: The brickIds of the entities we want to delete
        :param skip_validation_for_empty_values: Set this to True to ignore validation that required values are set
        :param raw_result: Set to True to get the raw result back (optional)
        :return:
        """
        query_method = getattr(self.client.service, method)

        result = query_method({
            'Credentials': self.credentials,
            'identify': self.identifier,
            'BrickIds': self.__argument_transform(brick_ids)
        })

        return result

    @staticmethod
    def get_response_rows(result: dict, method: str):
        """
        Gets response rows based on results object. Mitigates the plural form inconsistency present in the API
        :param result:
        :param method:
        :return:
        """
        if 'Result' in result.keys() and result['Result'] is not None:
            response_field = method + 'ResponseRow' \
                if method + 'ResponseRow' in result['Result'] \
                else method[:-1] + 'ResponseRow'
            if result['Result'][response_field] is not None:
                return result['Result'][response_field]

        if 'Entities' in result.keys() and result['Entities'] is not None:
            class_name = Bfs.__get_entity_class_name(method)
            response_field = class_name \
                if class_name in result['Entities'] \
                else class_name[:-1]
            if result['Entities'][response_field] is not None:
                return result['Entities'][response_field]

    @staticmethod
    def ordered_dict_to_object(value: dict):
        """
        Recursively gets an object based on an ordered dictionary that may contain lists
        :param value:
        :return:
        """

        if isinstance(value, list):
            a = []
            for item in value:
                a.append(Bfs.ordered_dict_to_object(item))
            return a

        if isinstance(value, OrderedDict):
            o = {}
            for key, value in value.items():
                o[key] = Bfs.ordered_dict_to_object(value)
            return o

        return value
