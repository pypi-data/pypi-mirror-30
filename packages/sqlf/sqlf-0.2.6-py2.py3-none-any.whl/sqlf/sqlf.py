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

################################################################################
# Globals / Initialisation
################################################################################
__connection = apsw.Connection(':memory:')
atexit.register(__connection.close)


################################################################################
# Public API
################################################################################

def sql(*, return_type=None):
    def _decorator(func):
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
                        tmp = dict(zip(columns, row))
                        yield return_type(tmp) if return_type else tmp
                except apsw.ExecutionCompleteError:
                    return
        return _wrapper
    return _decorator


def scalar_udf(func):
    __connection.createscalarfunction(func.__name__, func)
    return func

################################################################################
# Internals
################################################################################

def colname(desc):
    return '_'.join(re.findall('\w[\w\d]+', desc[0]))
