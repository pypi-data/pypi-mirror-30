# -*- coding: utf-8 -*-

''' SQL in F(unctions)

    udf_lib contains useful user-defined functions
'''

import cbor2
import re
import typeguard
import typing

################################################################################
# Text Processing
################################################################################

@typeguard.typechecked
def match(string1 : str, string2 : str) -> bool:
    return list(re.findall('[a-z0-9]+', string1.lower())) == \
           list(re.findall('[a-z0-9]+', string2.lower()))

@typeguard.typechecked
def number(string : str) -> typing.Union[int, float, None]:
    for tmp in re.finditer('\d+(\.\d+)?', string):
        tmp = tmp.group(0)
        if '.' in tmp:
            return float(tmp)
        else:
            return int(tmp)
        break


################################################################################
# Data Serialisation
################################################################################

@typeguard.typechecked
def cbor(obj) -> bytes:
    return cbor2.dumps(obj)

@typeguard.typechecked
def uncbor(string : bytes):
    return cbor2.loads(string)
