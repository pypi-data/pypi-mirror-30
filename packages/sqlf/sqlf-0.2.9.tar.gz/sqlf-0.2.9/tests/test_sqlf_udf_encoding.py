#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sqlf` package."""

# import pytest
import sqlf


###############################################################################
# Data Encoding UDFs
###############################################################################


def test_tohex():
    @sqlf.sqlf
    def _test(a):
        ''' select tohex(:a) as h; '''
    assert [{'h': '616263'}] == list(_test('abc'))


def test_base91_encode():
    @sqlf.single_row
    @sqlf.sqlf
    def test(txt):
        ''' select b91enc(:txt) as b91; '''
    assert {'b91': 'fPNKd'} == test('test')
    assert {'b91': 'fPNKd'} == test(b'test')


def test_base91_decode():
    @sqlf.single_row
    @sqlf.sqlf
    def test(b91):
        ''' select b91dec(:b91) as txt; '''
    assert {'txt': b'May a moody baby doom a yam?\n'} == \
        test('8D9Kc)=/2$WzeFui#G9Km+<{VT2u9MZil}[A')


def test_base91_reversible():
    @sqlf.single_row
    @sqlf.sqlf
    def test(txt):
        ''' select b91dec(b91enc(:txt)) as txt; '''
    assert {'txt': b'test123'} == test(b'test123')
