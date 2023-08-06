#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sqlf` package."""

# import pytest
import sqlf


###############################################################################
# Text Processing UDFs
###############################################################################


def test_similar():
    @sqlf.single_row
    @sqlf.sqlf
    def test(a):
        ''' select similar(:a, 'this-is-a-test') as m; '''
    assert {'m': True} == test('this is . @a test')
    assert {'m': False} == test('this ------ test')


def test_number():
    @sqlf.single_row
    @sqlf.sqlf
    def test(a):
        ''' select number(:a) as n; '''
    assert {'n': 3.14} == test('this costs 3.14 eur')
    assert {'n': 9999} == test('in year 9999 of counting')
