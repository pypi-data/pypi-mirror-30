# -*- coding: utf-8 -*-

"""Top-level package for SQL in F(unctions)."""

__author__ = """Digitalmensch"""
__email__ = 'contact@digitalmensch.ch'
__version__ = '0.2.8'

from .sqlf import sql
from .sqlf import scalar_udf
from .sqlf import single_row

# Activate built-in UDFs
from .udf_lib import similar
from .udf_lib import number
from .udf_lib import tohex
from .udf_lib import cbor
from .udf_lib import uncbor
from .udf_lib import nonce
from .udf_lib import sha3
scalar_udf(similar)
scalar_udf(number)
scalar_udf(tohex)
scalar_udf(cbor)
scalar_udf(uncbor)
scalar_udf(nonce)
scalar_udf(sha3)
del similar, number, tohex, cbor, uncbor, nonce, sha3

__all__ = [
    'sql',
    'scalar_udf',
]
