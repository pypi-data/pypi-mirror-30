import apsw
import inspect
import functools
import contextlib
import re

################################################################################
#
################################################################################

class sqldb(object):

    def __init__(self, sql=None, database=':memory:'):
        self.__db = apsw.Connection(database)
        if sql is not None:
            with contextlib.closing(self.__db.cursor()) as cur:
                cur.execute(sql)

    def sqludf(self, func):
        sig = inspect.signature(func)
        self.__db.createscalarfunction(func.__name__, func)

    def sqlfunc(self, _func=None, post=None, single=False, default=None):
        def _decorator(func):
            sql = func.__doc__
            assert len(sql) >= 8 # 'SELECT 1'
            signature = inspect.signature(func)
            params = tuple(signature.parameters.keys())

            @functools.wraps(func)
            def _function(*args, **kwargs):
                with contextlib.closing(self.__db.cursor()) as cur:
                    bound = signature.bind(*args, **kwargs)
                    bound.apply_defaults()
                    mapping = dict(zip(params, bound.args))

                    result = cur.execute(sql, mapping)

                    try:
                        description = result.getdescription()
                    except apsw.ExecutionCompleteError:
                        description = None
                        return default

                    if description:
                        keys = [
                            '_'.join(re.findall('\w[\w\d]+', attr[0]))
                            for attr in description
                        ]
                        result = map(lambda vals: dict(zip(keys, vals)), result)

                        if single:
                            for r in result:
                                return post(r) if post else r
                            else:
                                return default

                        else:
                            return list(map(post, result) if post else result)

                    else:
                        # self.__db.commit()
                        return self.__db.last_insert_rowid()

            return _function

        if _func is not None:
            return _decorator(_func)
        else:
            return _decorator
