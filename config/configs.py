"""
This module is used to easily use conf.yaml file.
It also contains methods to simplify main function
"""

from os import path
from typing import Any, List

import yaml

_CONF_PATH = path.join(path.dirname(__file__), path.pardir, 'conf.yaml')
_CONF = yaml.load(open(_CONF_PATH), Loader=yaml.FullLoader)


def get(key: str) -> Any:
    """
    Lookup the conf file for a property

    :param key: which property to lookup (using "." if looking for a nested property)
    :return: the found property
    :raise ValueError if key isn't found in conf file
    """
    levels = key.split('.')
    try:
        elem = _CONF  # iterative lookup for nested property
        for level in levels:
            elem = elem[level]
        return elem
    except KeyError:
        raise ValueError(f"Property missing in 'conf.yaml' file: {key}")


def get_filters() -> List:
    """
    Lookup the conf file for a filter property

    :return: a List containing all filters to get metrics about
    :raise ValueError if filters property isn't found in conf file
    """
    try:
        elem = _CONF
        filters = list()
        for flt in elem['filters']:
            filters.append(elem['filters'][flt][0]['name'])
            get_filters.__setattr__(f'{elem["filters"][flt][1]["groupByFields"]}', flt)
        return filters
    except KeyError:
        raise ValueError(f"Filters missing in 'conf.yaml' file")


def get_groubbyfield(metric_type) -> Any:
    """
    Lookup the conf file for groupBy field of a filter

    :param: metric_type: complete metric type name
    :return: a String which corresponds to the groupBy field of the filter
    :raise ValueError if groupBy field isn't found in conf file
    """
    try:
        elem = _CONF
        for flt in elem['filters']:
            if _CONF['filters'][flt][0]['name'] == metric_type:
                if elem['filters'][flt][1]['groupByFields'] is None:
                    return None
                else:
                    return elem['filters'][flt][1]['groupByFields']
    except KeyError:
        raise ValueError(f"groupByField property missing in 'conf.yaml' file")
