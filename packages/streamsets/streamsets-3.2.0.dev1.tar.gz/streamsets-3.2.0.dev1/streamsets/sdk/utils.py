# Copyright 2017 StreamSets Inc.

"""Assorted utility functions."""

import base64
import logging
import random
import re
from collections import OrderedDict
from datetime import datetime

from inflection import camelize

logger = logging.getLogger(__name__)


def get_random_string(characters, length=8):
    """
    Returns a string of the requested length consisting of random combinations of the given
    sequence of string characters.
    """
    return ''.join(random.choice(characters) for _ in range(length))


def join_url_parts(*parts):
    """
    Join a URL from a list of parts. See http://stackoverflow.com/questions/24814657 for
    examples of why urllib.parse.urljoin is insufficient for what we want to do.
    """
    return '/'.join([piece.strip('/') for piece in parts])


def get_params(parameters, exclusions=None):
    """Get a dictionary of parameters to be passed as requests methods' params argument.

    The typical use of this method is to pass in locals() from a function that wraps a
    REST endpoint. It will then create a dictionary, filtering out any exclusions (e.g.
    path parameters) and unset parameters, and use camelize to convert arguments from
    ``this_style`` to ``thisStyle``.
    """
    return {camelize(arg, uppercase_first_letter=False): value
            for arg, value in parameters.items()
            if value is not None and arg not in exclusions}


class Version:
    """Maven version string abstraction.

    Use this class to enable correct comparison of Maven versioned projects. For our purposes,
    any version is equivalent to any other version that has the same 4-digit version number (i.e.
    3.0.0.0-SNAPSHOT == 3.0.0.0-RC2 == 3.0.0.0).

    Args:
        version (`str`): Version string (e.g. '2.5.0.0-SNAPSHOT')
    """
    # pylint: disable=protected-access,too-few-public-methods
    def __init__(self, version):
        self._str = version

        # Generate a tuple of versions by padding the given version to have 4 numbers (e.g. '2.5' => '2.5.0.0-SNAPSHOT'
        # and '2.5-SNAPSHOT' => '2.5.0.0-SNAPSHOT'). We do this in a bit of a gross way using slice notation to insert
        # the correct number of zeros at the end of the list (or before the last element, if the last element is
        # the 'SNAPSHOT' specifier.
        version_list = [int(i) if i.isdigit() else i for i in re.split('[.-]', self._str)]
        lvl = len(version_list)
        version_list[lvl if version_list[-1] != 'SNAPSHOT' else lvl - 1:
                     lvl if version_list[-1] != 'SNAPSHOT' else lvl - 1] = (
                         [0] * (4 - (lvl if version_list[-1] != 'SNAPSHOT' else lvl - 1))
                     )
        self._tuple = tuple(version_list)

    def __repr__(self):
        return str(self._tuple)

    def __eq__(self, other):
        return self._tuple[:4] == other._tuple[:4]

    def __lt__(self, other):
        if not isinstance(other, Version):
            raise TypeError('Comparison can only be done for two Version instances.')
        return self._tuple[:4] < other._tuple[:4]

    def __gt__(self, other):
        return other.__lt__(self)

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def __le__(self, other):
        return other.__ge__(self)


def sdc_value_reader(value):
    """Helper function which can parse SDC Record value (Record JSON in dict format for example)
    and convert to SDC implied Python collection with necessary types being converted from SDC
    to Python.

    Args:
        value: SDC Record value.

    Returns:
        The value.
    """
    # Note: check instance of OrderedDict before dict to avoid superfluous
    # check of OrderedDict getting evaluated for dict
    if isinstance(value, OrderedDict):
        return OrderedDict([(value['dqpath'].split('/')[-1], sdc_value_reader(value))
                            for key, value in value.items()])
    elif isinstance(value, dict):
        if 'type' in value:
            if value['value'] is None:
                return value['value']
            elif value['type'] == 'LIST_MAP':
                return sdc_value_reader(OrderedDict([(key, value['value'][key])
                                                     for key in range(len(value['value']))]))
            elif value['type'] in ('LIST', 'MAP'):
                return sdc_value_reader(value['value'])
            elif value['type'] in ('SHORT', 'INTEGER', 'LONG'):
                return int(value['value'])
            elif value['type'] in ('CHAR', 'STRING'):
                return value['value']
            elif value['type'] in ('DATE', 'DATETIME', 'TIME'):
                return datetime.utcfromtimestamp(value['value']/1000)
            elif value['type'] == 'BOOLEAN':
                return value['value']
            elif value['type'] == 'BYTE':
                return str(value['value']).encode()
            elif value['type'] in ('DOUBLE', 'FLOAT', 'DECIMAL'):
                return float(value['value'])
            elif value['type'] == 'BYTE_ARRAY':
                return base64.b64decode(value['value'])
            else:
                return value['value']
        else:
            return {key: sdc_value_reader(value) for key, value in value.items()}
    elif isinstance(value, list):
        return [sdc_value_reader(item) for item in value]
    else:
        return value['value']


def pipeline_json_encoder(o):
    """Default method for JSON encoding of custom classes."""
    if hasattr(o, '_data'):
        return o._data
    raise TypeError('{} is not JSON serializable'.format(repr(o)))


def format_log(log_records):
    return '\n'.join([('{timestamp} [user:{user}] [pipeline:{entity}] '
                       '[runner:{runner}] [thread:{thread}] {severity} '
                       '{category} - {message} {exception}').format(timestamp=rec.get('timestamp'),
                                                                    user=rec.get('s-user'),
                                                                    entity=rec.get('s-entity'),
                                                                    runner=rec.get('s-runner'),
                                                                    thread=rec.get('thread'),
                                                                    severity=rec.get('severity'),
                                                                    category=rec.get('category'),
                                                                    message=rec.get('message'),
                                                                    exception=rec.get('exception'))
                      for rec in log_records])
