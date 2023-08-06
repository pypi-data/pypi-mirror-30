# -*- coding: utf-8 -*-

''' SQL in F(unctions)

    udf_lib contains useful user-defined functions
'''


import cbor2
import typeguard
import typing


###############################################################################
# Data Serialisation
###############################################################################


def cbor_map() -> bytes:
    return cbor2.dumps(dict())


def cbor_list() -> bytes:
    return cbor2.dumps(list())


@typeguard.typechecked
def cbor_insert(obj: bytes, key: typing.Any, value: typing.Any) -> bytes:
    tmp = cbor2.loads(obj)
    if isinstance(tmp, dict):
        tmp[key] = value
        return cbor2.dumps(tmp)
    if isinstance(tmp, list):
        tmp.insert(key, value)
        return cbor2.dumps(tmp)
    raise TypeError('cbor object must be map or list')


@typeguard.typechecked
def cbor_append(obj: bytes, value: typing.Any) -> bytes:
    tmp = cbor2.loads(obj)
    tmp.append(value)
    return cbor2.dumps(tmp)


@typeguard.typechecked
def cbor_has(obj: bytes, key: typing.Any) -> bool:
    tmp = cbor2.loads(obj)
    if isinstance(tmp, dict):
        return key in tmp
    if isinstance(tmp, list):
        return key in tmp
    raise TypeError('cbor object must be map or list')


@typeguard.typechecked
def cbor_get(obj: bytes, key: typing.Any) -> typing.Any:
    tmp = cbor2.loads(obj)
    if isinstance(tmp, dict):
        return tmp[key]
    if isinstance(tmp, list):
        return tmp[key]
    raise TypeError('cbor object must be map or list')
