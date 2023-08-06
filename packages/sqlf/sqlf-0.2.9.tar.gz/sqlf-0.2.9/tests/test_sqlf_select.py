#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sqlf` package."""

# import pytest
import sqlf


###############################################################################
# sqlf.sql with SELECT
###############################################################################


def test_return_single_value_row():
    @sqlf.single_row
    @sqlf.sqlf
    def test():
        ''' select 1 as one; '''
    assert {'one': 1} == test()


def test_return_two_values_row():
    @sqlf.single_row
    @sqlf.sqlf
    def test():
        ''' select 1 as one, 2 as two; '''
    assert {'one': 1, 'two': 2} == test()


def test_return_from_two_selects():
    @sqlf.sqlf
    def test():
        ''' select 1 as one;
            select 2 as one;
        '''
    tmp = list(test())
    assert {'one': 1} in tmp
    assert {'one': 2} in tmp


def test_two_value_returns_from_two_selects():
    @sqlf.sqlf
    def test():
        ''' select 1.0 as one, 2.0 as two;
            select 1.1 as one, 2.1 as two;
        '''
    tmp = list(test())
    assert {'one': 1.0, 'two': 2.0} in tmp
    assert {'one': 1.1, 'two': 2.1} in tmp


def test_various_returns_from_many_selects():
    @sqlf.sqlf
    def test():
        ''' select 1 as one;
            select 2 as two;
            select 3 as three, 4 as four;
        '''
    tmp = list(test())
    print(tmp)
    assert {'one': 1} in tmp
    assert {'two': 2} in tmp
    assert {'three': 3, 'four': 4} in tmp


def test_return_from_table():
    @sqlf.sqlf
    def test():
        ''' create table test_table (a, b, c);
            insert into test_table values (1, 2, 3);
            insert into test_table values (2, 3, 4);
            select a+b as d, b+c as e from test_table;
            drop table test_table;
        '''
    tmp = list(test())
    assert {'d': 3, 'e': 5} in tmp
    assert {'d': 5, 'e': 7} in tmp
