# -*- coding: utf-8 -*-

''' SQL in F(unctions)

    udf_lib contains useful user-defined functions
'''

import cbor2
import hashlib
import os
import re
import typeguard
import typing

###############################################################################
# Text Processing
###############################################################################


@typeguard.typechecked
def similar(string1: str, string2: str) -> bool:
    return list(re.findall('[a-z0-9]+', string1.lower())) == \
           list(re.findall('[a-z0-9]+', string2.lower()))


@typeguard.typechecked
def number(string: str) -> typing.Union[int, float, None]:
    for tmp in re.finditer('\d+(\.\d+)?', string):
        tmp = tmp.group(0)
        if '.' in tmp:
            return float(tmp)
        else:
            return int(tmp)
        break


###############################################################################
# Data Encodings
###############################################################################


@typeguard.typechecked
def _binary(data: typing.Union[str, bytes]) -> bytes:
    if isinstance(data, str):
        return data.encode('utf-8')
    return data


@typeguard.typechecked
def tohex(data: typing.Union[str, bytes]) -> str:
    return _binary(data).hex()


###############################################################################
# Data Serialisation
###############################################################################


@typeguard.typechecked
def cbor(obj) -> bytes:
    return cbor2.dumps(obj)


@typeguard.typechecked
def uncbor(string: bytes):
    return cbor2.loads(string)


###############################################################################
# Cryptography
###############################################################################


@typeguard.typechecked
def nonce(n: int = 64) -> bytes:
    return os.urandom(n)


@typeguard.typechecked
def sha3(data: typing.Union[str, bytes]) -> bytes:
    return hashlib.sha3_512(_binary(data)).digest()
