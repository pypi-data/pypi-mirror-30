# -*- coding: utf-8 -*-

''' SQL in F(unctions)

    SQL in Python __doc__-strings as an alternative to ORMs
'''

import apsw
import atexit
import contextlib
import functools
import inspect
import re

###############################################################################
# Globals / Initialisation
###############################################################################
__connection = apsw.Connection(':memory:')
atexit.register(__connection.close)


###############################################################################
# Public API
###############################################################################


def sql(func):
    ''' the magical function decorator '''
    sql = func.__doc__
    signature = inspect.signature(func)
    params = tuple(signature.parameters.keys())

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        with contextlib.closing(__connection.cursor()) as cursor:
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            mapping = dict(zip(params, bound.args))
            cursor.execute(sql, mapping)
            try:
                columns = list(map(colname, cursor.getdescription()))
                for row in cursor:
                    yield dict(zip(columns, row))
            except apsw.ExecutionCompleteError:
                return
    return _wrapper


def scalar_udf(func):
    __connection.createscalarfunction(func.__name__, func)
    return func


def single_row(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        for row in func(*args, **kwargs):
            return row
    return _wrapper

###############################################################################
# Internals
###############################################################################


def colname(desc):
    return '_'.join(re.findall('\w[\w\d]*', desc[0]))
