# -*- coding: utf-8 -*-
"""OpenMaker module for survey data schema.

This module contains functions and classes which can be used an
editing interface to a predesigned JSON schema.

Todo:
    * Do the Sphinx documentation
    * Improve inplace editing methods.
    
"""

import json
import os,sys,getopt


def inspect(args=None):
    """A command-line entry point in order to list major fields of an input schema.

    """

    if args is None:
        argv = sys.argv[1:]
    else:
        argv = args
        
    params = ['fields-top', 'fields-all', 'fields-required', 'questions']
    help_msg = 'inspect \{one of: {} \} -s <schemafile>'.format(params)
 
    if len(argv) < 4:
        print(help_msg)
        sys.exit(1)

    if not argv[0] == 'inspect':
        print(help_msg)
        sys.exit(1)

    argv = argv[1:]

    if argv[0] not in params:
        print(help_msg)
        sys.exit(1)
        
    param = argv[0]
    argv = argv[1:]

    schema_file = ''
    try:
        opts, args = getopt.getopt(argv,"hs:",["sfile="])
    except getopt.GetoptError:
        print(help_msg)
        sys.exit(1)
        
    for opt, arg in opts:
        if opt == '-h':
            print(help_msg)
            sys.exit()
        elif opt in ("-s", "--sfile"): schema_file = arg

    S = Schema()
    S.load_from_file(schema_file)

    if param == 'fields-top':
        response = S.get_fields(main_only = True)
        print(response)
        sys.exit()
    elif param == 'fields-all':
        response = S.get_fields()
        print(response)
        sys.exit()
    elif param == 'fields-required':
        response = S.get_required_fields()
        print(response)
        sys.exit()
    elif param == 'questions':
        response = S.get_questionaire_matches()
        print(response)
        sys.exit()
    else:
        print(help_msg)
        sys.exit(1)

def get_field_names(schema):
    """The method lists all of the fields of a given schema. It parses the entire schema in JSON format.

        Args:
            schema (:obj:`JSON`): A JSON object which describes the schema (default None).
            
        Returns:
            (:obj:`list` of :obj:`string`): list of field names.
    """
    
    def get_fields_from_schema(schema, fields = []):
        """The method lists all of the fields of of list of schemas.

        Args:
            schema (:obj:`JSON`): A list of JSON schemas.

        Returns:
            (:obj:`list` of :obj:`string`): list of field names.

        Raises:
            OMSchemaUnknown: Raised if an unknown object type in the given schema is encountered.
            OMSchemaKeyError: Raised if a corrupted key within the schema is encountered.

        """

        if not schema:
            return fields

        if 'type' not in schema.keys():
            msg = 'And invalid schema has been encountered.'
            code = 201
            raise SchemaInvalidType(msg,code)

        if schema['type'] in ['integer', 'string']:
            fields.append(schema['$id'])
            return fields

        if schema['type'] == 'array':
            schema = schema['items']
            return get_fields_from_schema(schema, fields)

        if schema['type'] == 'object':
            schemas = list(schema['properties'].values())
            return get_fields_from_schemas(schemas, fields)

        msg = 'An unknown object type encountered: {}'.format(schema['type'])
        code = 101
        raise SchemaUnknownError(msg,code)

    def get_fields_from_schemas(schemas, fields = []):
        """The method lists all of the fields of of list of schemas.

        Args:
            schema (:obj:`list` of :obj:`JSON`): A list of JSON schemas.

        Returns:
            (:obj:`list` of :obj:`string`): list of field names.

        """
        if not schemas: return fields
        schema = schemas.pop(0)
        get_fields_from_schema(schema, fields)
        return get_fields_from_schemas(schemas, fields)

    return get_fields_from_schema(schema, fields = [])

class OMSchemaUnknown(Exception):
    """OpenMaker data schema error for unknown object types.

    Args:
        msg (str): Human readable string describing the exception.
        code (:obj:`int`, optional): Error code.

    Attributes:
        msg (str): Human readable string describing the exception.
        code (int): Exception error code.

    """

    def __init__(self, msg, code):
        self.msg = msg
        self.code = code

class OMSchemaKeyError(Exception):
    """OpenMaker data schema error for invalid key types.

    Args:
        msg (str): Human readable string describing the exception.
        code (:obj:`int`, optional): Error code.

    Attributes:
        msg (str): Human readable string describing the exception.
        code (int): Exception error code.

    """

    def __init__(self, msg, code):
        self.msg = msg
        self.code = code


class Schema(object):
    """A generic interface object for JSON Schemas of OpenMaker Project.

    Attributes:
        schema_file (:obj:`string`): A file path to a JSON schema file.
        
    """
    schema_file = None
    
    def __init__(self, schema = None):
        """The class constructor.

        Args:
            schema (:obj:`JSON`): A JSON object which describes the schema (default None).

        """
        self.schema = schema
        self._update_mappings()
    
    def load(self, schema):
        """The method loads a schema from a JSON object.
        
        Args:
            fname (:obj:`dict`): The JSON document in dictionary format.
            
        Returns:
            bool: True.

        """
        self.schema = schema
        self._update_mappings()
        return True
        
    def load_from_file(self, fname):
        """The method loads a schema from a file path to a JSON schema file.
        
        Args:
            fname (str): The file path.
            
        Returns:
            bool: True if successful, False otherwise.

        Raises:
            FileNotFoundError: Raised if a given file is not accessable.

        """
        schema = None
        with open(fname, "r") as f:
            schema = json.load(f)
        if not schema: return False
        self.schema = schema
        self.schema_file = fname
        self._update_mappings()
        return True
    
    def get_fields(self, schema=None, main_only = False):
        """The method lists all of the fields of a given schema. It parses the entire 
            schema in JSON format.
        
        Args:
            schema (:obj:`JSON`): A JSON object which describes the schema (default None).
            
        Returns:
            (:obj:`list` of :obj:`string`): list of field names.
            
        """
        fields = []
        if not schema:
            schema = self.schema
            self._update_mappings()
        if main_only:
            fields = list(schema['properties'].keys()) if 'properties' in schema.keys() else []
            return fields
        
        fields = list(self._fmap.keys())
        return fields

    def _update_mappings(self):
        """The method calls the crawler for field, question and path matchings.

        Note:
            It must be called everytime a non-empty schema is loaded.                    
        Returns:
            (Bool): Returns true when succeeded.
            
        """            
        self._paths = Schema._get_fields_from_schema(self.schema, fields = [])
        self._extract_fields_matching()
        return True
    
    def get_questionaire_matches(self):
        """The method lists all of the fields of a given schema. It parses the entire 
            schema in JSON format.
        
        Args:
            schema (:obj:`JSON`): A JSON object which describes the schema (default None).
            
        Returns:
            (:obj:`list` of :obj:`string`): list of field names.
            
        """
        
        if not self.schema:
            msg = 'No schema found!. Load a schema first.'
            code = 102
            raise OMSchemaUnknown(msg,code)
        
        return {k:v['no'] for k,v in self._fmap.items()}
    
    def _extract_fields_matching(self):
        self._fmap = dict()
        for p,q in self._paths:
            k = p.replace('/items/properties/', '*')
            k = p.replace('/items', '*')
            k = k.replace('/properties/', '.')
            k = k.strip('.')
            q = q.strip()
            self._fmap[k ] = {'path':p, 'no':q}
        return True
            
        
        
    def get_required_fields(self, schema=None):
        """The method lists all the required fields of a given schema. It parses the entire 
            schema in JSON format.
        
        Args:
            schema (:obj:`JSON`): A JSON object which describes the schema (default None).
            
        Returns:
            (:obj:`list` of :obj:`string`): list of field names.
            
        """
        
        if not schema: schema = self.schema
        required = schema['required'] if 'required' in schema.keys() else []
        return required
    
    @staticmethod
    def _get_fields_from_schema(schema, fields = []):
        """The method lists all of the fields of of list of schemas.

        Args:
            schema (:obj:`JSON`): A list of JSON schemas.

        Returns:
            (:obj:`list` of :obj:`string`): list of field names.

        Raises:
            OMSchemaUnknown: Raised if an unknown object type in the given schema is encountered.
            OMSchemaKeyError: Raised if a corrupted key within the schema is encountered.

        """

        if not schema:
            return fields

        if 'type' not in schema.keys():
            msg = 'And invalid schema has been encountered.'
            code = 201
            raise OMSchemaKeyError(msg,code)

        if schema['type'] in ['integer', 'string']:
            fields.append((schema['$id'],schema['description']))
            return fields

        if schema['type'] == 'array':
            schema = schema['items']
            return Schema._get_fields_from_schema(schema, fields)

        if schema['type'] == 'object':
            schemas = list(schema['properties'].values())
            return Schema._get_fields_from_schemas(schemas, fields)

        msg = 'An unknown object type encountered: {}'.format(schema['type'])
        code = 101
        raise OMSchemaUnknown(msg,code)

    @staticmethod
    def _get_fields_from_schemas(schemas, fields = []):
        """The method lists all of the fields of of list of schemas.

        Args:
            schema (:obj:`list` of :obj:`JSON`): A list of JSON schemas.

        Returns:
            (:obj:`list` of :obj:`string`): list of field names.

        """
        if not schemas: return fields
        schema = schemas.pop(0)
        Schema._get_fields_from_schema(schema, fields)
        return Schema._get_fields_from_schemas(schemas, fields)

if __name__ == '__main__':
    pass
