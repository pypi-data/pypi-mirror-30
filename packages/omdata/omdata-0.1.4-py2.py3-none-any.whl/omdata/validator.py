# -*- coding: utf-8 -*-
"""OpenMaker schema validator.

This module, until a fully custom version of it to be developed, uses jsonschema
package for validation of survey response against openmaker design.

Example:
    .. code-block:: bash

        python validator.py -q omsurvey.json -s omsurvey.schema

Todo:
    * Do the Sphinx documentation

"""

from jsonschema import validate
import json, sys, getopt


def check_json(survey, schema):
    """The method checks validity of an input json against the schema.

    Args:
        survey (:obj:`JSON`): A JSON object.
        schema (:obj:`JSON`): A JSON schema.

    Returns:
        (:obj:`bool`): Returns `True` when it is validated.

    """
    validity = True
    try:
        validate(survey,schema)
    except:
        validity = False
    return validity

def check_file(survey_file, schema_file):
    """Given external files the method checks validity of an input json file
        against the schema file.

    Args:
        survey (:obj:`string`): A JSON data file.
        schema (:obj:`string`): A JSON schema file.

    Returns:
        (:obj:`bool`): True.

    """

    with open(schema_file) as scf:
        schema = json.load(scf)
    with open(survey_file) as suf:
        survey = json.load(suf)
    return check_json(survey,schema)


def main(argv):
    """The driver function when the module is run as a standalone python script.

    """
    help_msg = 'python validator.py -q <surveyfile> -s <schemafile>'
    if not argv:
        print(help_msg)
        sys.exit(2)
        
    survey_file = ''
    schema_file = ''
    try:
        opts, args = getopt.getopt(argv,"hq:s:",["qfile=","sfile="])
    except getopt.GetoptError:
        print(help_msg)
        sys.exit(2)
        
    for opt, arg in opts:
        if opt == '-h':
            print(help_msg)
            sys.exit()
        elif opt in ("-q", "--qfile"): survey_file = arg
        elif opt in ("-s", "--sfile"): schema_file = arg

    checked = check_file(survey_file, schema_file)
    if checked:
        print("Congratulations {} is a valid survey data.".format(survey_file))
    else:
        print("Validation has failed. Please check the data.")
    
if __name__ == '__main__':
    main(sys.argv[1:])

