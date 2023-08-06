#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sqlf` package."""

import pytest
import sqlf
import types


###############################################################################
# sqlf.sqlf
###############################################################################


def test_sql_function():
    @sqlf.sqlf
    def test():
        ''' select 1 as one; '''
    assert test is not None
    assert isinstance(test, types.FunctionType)


def test_sql_function_yields_generator():
    @sqlf.sqlf
    def test():
        ''' select 1 as one; '''
    tmp = test()
    assert tmp is not None
    assert isinstance(tmp, types.GeneratorType)


@pytest.mark.parametrize("value", [(1, 3.14, '', b'', None, [], {})])
def test_sqlf_decorator_takes_function(value):
    with pytest.raises(TypeError):
        sqlf.sqlf(value)


###############################################################################
# sqlf.scalar_udf
###############################################################################


def test_scalar_udf_returns_function():
    def one():
        return 1
    two = sqlf.scalar_udf(one)
    assert one is two


def test_scalar_udf_registers_function():
    @sqlf.scalar_udf
    def one():
        return 1

    @sqlf.sqlf
    def _select_one():
        ''' select one() as one; '''
    assert [{'one': 1}] == list(_select_one())


###############################################################################
# sqlf.aggregate_udf
###############################################################################


def test_aggregate_udf_returns_same():
    class agg(object):
        def step(self, *args):
            pass

        def final(self, *args):
            return 1
    tmp = sqlf.aggregate_udf(agg)
    assert tmp is agg


def test_aggregate_udf_registers_function():
    @sqlf.aggregate_udf
    class agg(object):
        def step(self, *args):
            pass

        def final(self, *args):
            return 1

    @sqlf.sqlf
    def test():
        ''' select agg() as one; '''
    assert [{'one': 1}] == list(test())


def test_aggregate_udf_can_be_used_in_query():
    @sqlf.aggregate_udf
    class agg(object):
        def __init__(self):
            self.val = 1

        def step(self, *args):
            self.val /= 2.0

        def final(self, *args):
            return self.val

    @sqlf.sqlf
    def test():
        ''' create table test_table (a);
            insert into test_table values (1);
            insert into test_table values (2);
            insert into test_table values (3);
            select agg(a) as one from test_table;
            drop table test_table;
        '''
    assert [{'one': 0.125}] == list(test())


###############################################################################
# sqlf.single_row
###############################################################################


@pytest.mark.parametrize("value", [1, 3.14, '', b'', None, [], {}])
def test_single_row_takes_generator_function(value):
    def it():
        yield {'one': 1}
    with pytest.raises(TypeError):
        sqlf.single_row(value)
    assert sqlf.single_row(it)() is not None


def test_single_row_returns_first_row():
    def it():
        yield {'one': 1}
        yield {'two': 2}
    val = sqlf.single_row(it)()
    assert 'one' in val
    assert val['one'] == 1


###############################################################################
# sqlf.as_type
###############################################################################


def test_as_type():
    @sqlf.as_type(lambda **kw: tuple(kw.keys()))
    @sqlf.sqlf
    def _test():
        ''' select 3.14 as pi, 11 as eleven; '''
    tmp = list(_test())[0]
    assert len(tmp) == 2
    assert 'pi' in tmp
    assert 'eleven' in tmp
