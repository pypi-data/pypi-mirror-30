"""
Title:
    Python script for reading a C file

Assumption:
    1. All the python packages are installed
    2. You are using python==3.5
    3. Any more assumptions <>

Description:
    1. Describe the class

Author:
    Abhijit Bansal

"""

# **************************
# region GLOBAL IMPORTS
import os
import argparse

import sys
from google.protobuf import text_format, json_format
import logging
from pathlib2 import Path

# endregion
# **************************

# **************************
# region LOCAL IMPORTS

import log

# endregion
# **************************

# For logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ProtoToolsError(Exception):
    pass


def proto_from_file(file_path, proto_type):
    """
    To read a proto message from a human readable file format

    Args:
        proto_type (object): The proto message class
        file_path (str): To read a proto message from human readable form like .txt or .json
    """
    with open(str(file_path)) as r:
        if Path(file_path).suffix.lower() == 'json':
            return json_format.Parse(r.read(), proto_type())
        else:
            return text_format.Merge(r.read(), proto_type())


def show_proto(proto_message, default_fields=False, json=False):
    """
    To convert a proto message to a human readable form and display on screen

    Args:
        json (bool): To display in json format
        default_fields (bool): To show even default fields
        proto_message (object):  The proto message that needs to be written to a human readable file
    """
    if json:
        return json_format.MessageToJson(proto_message, including_default_value_fields=default_fields)
    else:
        return text_format.MessageToString(proto_message)


def proto_to_file(proto_message, file_path, default_fields=False):
    """
    To convert a proto message to a human readable form and write to a file

    Args:
        default_fields (bool): To show even default fields
        file_path (str): The file path with extension like json or text for human readable form of proto message
        proto_message (object):  The proto message that needs to be written to a human readable file
    """
    with open(str(file_path), 'wb') as w:
        if Path(file_path).suffix.lower() == 'json':
            w.write(json_format.MessageToJson(proto_message, including_default_value_fields=default_fields))
        else:
            w.write(text_format.MessageToString(proto_message))


def proto_from_stream(file_path, proto_type):
    """
    To read a proto message from stream

    Args:
        proto_type (object): The proto message class
        file_path (str): To read a proto message from serialised stream
    """
    proto_message = proto_type()
    with open(str(file_path), 'rb') as r:
        logger.info('Deserializing from proto format')
        proto_message.ParseFromString(r.read())
        return proto_message


def proto_to_stream(proto_message, file_path):
    """
    To convert a proto message to a file

    Args:
        file_path (str): The out file
        proto_message (object): The proto message that needs to be serialised to file
    """
    logger.info("Processing {file_path}".format(**locals()))
    with open(str(file_path), 'wb') as w:
        w.write(proto_message.SerializeToString())


def validate_proto_enum(enum, value, description):
    """
    Validate that a string is a valid value for the enum, and return the corresponding number.

    Args:
        enum (A google protocol buffer enum object):  A specific class of enum which is basically key,value pair lookups
            similar to a dictionary
        value (str): string name of the item inside the enum
        description (str):  Description to use for error message if needed

    """
    if value in enum.values_by_name:
        return enum.values_by_name[value].number

    # the string was not in the list of names, print what was attempted
    error_string = 'Invalid {} 1 input:{}, enum: {} \n\tvalid values:'.format(description, value, enum.name)
    for key, value in enum.values_by_name.iteritems():
        error_string += '\n\t{} -> {}'.format(key, value.number)
    logger.error(error_string)
    return False


def main():
    """
    To encode/decode proto messages
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help="input file path")

    parser.add_argument('-IPATH', '--proto_path', type=str, default='',
                        help='Directory where all the proto files are available')

    parser.add_argument("--encode", type=str, default='', help="name of protobuf message")
    parser.add_argument("--decode", type=str, default='', help="name of protobuf message")

    parser.add_argument("-d", "--display", help="output item to the console", action="store_true")
    parser.add_argument("-a", "--allfields", help="To show all fields", action="store_true")
    parser.add_argument("-json", "--json", help="To decode to json", action="store_true")

    # Get args
    args = parser.parse_args()
    file_path = Path(args.file_path)
    proto_path = Path(args.proto_path if args.proto_path else os.getcwd())
    encode = args.encode
    decode = args.decode
    display = args.display
    all_fields = args.allfields
    json = args.json

    logger = log.setup_console_logger("protobuf_tools", logging.INFO)
    logger.setLevel(logging.DEBUG)

    # Validate and import all proto files
    if not proto_path.is_dir():
        ProtoToolsError("{proto_path} is not a valid directory".format(**locals()))

    # Get encode/decode
    message = ''
    to_proto = False
    if not encode and not decode:
        ProtoToolsError("No message name defined for encode/decode")
    elif encode:
        message = encode
        to_proto = True
    else:
        message = decode
        to_proto = False

    # Import all proto_files
    proto_type = None
    for f in proto_path.glob("*_pb2.py"):
        sys.path.append(str(f.parent))
        proto_pb2 = __import__(str(f.stem))
        try:
            proto_type = getattr(proto_pb2, message)
        except AttributeError as e:
            pass
        else:
            # if proto messages is found break out of loop
            break
    else:
        # If no message is found raise exception
        ProtoToolsError("{message} not found in the proto directory - {proto_path}".format(**locals()))

    if to_proto:
        proto_message = proto_from_file(file_path, proto_type)
        if display:
            print show_proto(proto_message, all_fields, json)
        else:
            proto_to_stream(proto_message, str(file_path.with_suffix(".protoout")))
        logger.info('success')
    else:
        proto_message = proto_from_stream(file_path, proto_type)
        if display:
            print show_proto(proto_message, default_fields=all_fields, json=json)
        else:
            if json:
                out_file_path = file_path.with_suffix(".json")
            else:
                out_file_path = file_path.with_suffix(".txt")
            proto_to_file(proto_message, out_file_path, default_fields=all_fields)
        logger.info('success')


if __name__ == "__main__":

    main()
