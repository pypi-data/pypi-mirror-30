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
import typeguard
import types

###############################################################################
# Globals / Initialisation
###############################################################################
__connection = apsw.Connection(':memory:')
atexit.register(__connection.close)


###############################################################################
# Public API
###############################################################################


@typeguard.typechecked
def sqlf(func: types.FunctionType):
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
            print(sql, mapping)
            cursor.execute(sql, mapping)
            try:
                for row in cursor:
                    columns = list(map(colname, cursor.getdescription()))
                    yield dict(zip(columns, row))
            except apsw.ExecutionCompleteError:
                return
    return _wrapper


@typeguard.typechecked
def scalar_udf(func: types.FunctionType):
    __connection.createscalarfunction(func.__name__, func)
    return func


def aggregate_udf(cls):
    def _factory():
        return cls(), cls.step, cls.final
    __connection.createaggregatefunction(cls.__name__, _factory)
    return cls


@typeguard.typechecked
def single_row(func: types.FunctionType):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        for row in func(*args, **kwargs):
            if not isinstance(row, dict):
                raise TypeError('requires dict')
            return row
    return _wrapper


def as_type(type_):
    @typeguard.typechecked
    def _decorator(func: types.FunctionType):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            for row in func(*args, **kwargs):
                yield type_(**row)
        return _wrapper
    return _decorator


###############################################################################
# Internals
###############################################################################


def colname(desc):
    return '_'.join(re.findall('\w[\w\d]*', desc[0]))
