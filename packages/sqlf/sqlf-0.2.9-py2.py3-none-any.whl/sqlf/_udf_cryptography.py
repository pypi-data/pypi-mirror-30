# -*- coding: utf-8 -*-

''' SQL in F(unctions)

    udf_lib contains useful user-defined functions
'''


import hashlib
import os
import typeguard
import typing
from ._udf_encoding import _binary


###############################################################################
# Cryptography
###############################################################################


@typeguard.typechecked
def nonce(n: int = 64) -> bytes:
    return os.urandom(n)


@typeguard.typechecked
def sha3(data: typing.Union[str, bytes]) -> bytes:
    return hashlib.sha3_512(_binary(data)).digest()
