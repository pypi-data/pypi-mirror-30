# -*- coding: utf-8 -*-

''' SQL in F(unctions)

    udf_lib contains useful user-defined functions
'''


import base91
import typeguard
import typing


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


@typeguard.typechecked
def b91enc(data: typing.Union[str, bytes]) -> str:
    return base91.encode(_binary(data))


@typeguard.typechecked
def b91dec(data: str) -> bytes:
    return bytes(base91.decode(data))
