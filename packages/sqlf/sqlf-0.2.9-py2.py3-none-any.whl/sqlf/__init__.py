# -*- coding: utf-8 -*-

"""Top-level package for SQL in F(unctions)."""

__author__ = """Digitalmensch"""
__email__ = 'contact@digitalmensch.ch'
__version__ = '0.2.9'

from ._sqlf import sqlf
from ._sqlf import scalar_udf
from ._sqlf import aggregate_udf
from ._sqlf import single_row
from ._sqlf import as_type

# Activate built-in UDFs
from ._udf_text import similar
from ._udf_text import number
from ._udf_encoding import tohex
from ._udf_encoding import b91enc
from ._udf_encoding import b91dec
from ._udf_cryptography import nonce
from ._udf_cryptography import sha3
from ._udf_serialisation import cbor_map
from ._udf_serialisation import cbor_list
from ._udf_serialisation import cbor_insert
from ._udf_serialisation import cbor_append
from ._udf_serialisation import cbor_has
from ._udf_serialisation import cbor_get


scalar_udf(similar)
scalar_udf(number)
scalar_udf(tohex)
scalar_udf(b91enc)
scalar_udf(b91dec)
scalar_udf(nonce)
scalar_udf(sha3)
scalar_udf(cbor_map)
scalar_udf(cbor_list)
scalar_udf(cbor_insert)
scalar_udf(cbor_append)
scalar_udf(cbor_has)
scalar_udf(cbor_get)


del similar
del number
del tohex
del b91enc
del b91dec
del nonce
del sha3
del cbor_map
del cbor_list
del cbor_insert
del cbor_append
del cbor_has
del cbor_get

__all__ = [
    'sqlf',
    'scalar_udf',
    'aggregate_udf',
    'single_row',
    'as_type',
]
