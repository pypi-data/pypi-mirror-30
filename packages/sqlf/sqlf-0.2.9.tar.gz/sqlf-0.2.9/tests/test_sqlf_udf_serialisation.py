#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sqlf` package."""

# import pytest
import sqlf


###############################################################################
# Data Serialisation UDFs
###############################################################################


def test_cbor_map():
    @sqlf.single_row
    @sqlf.sqlf
    def test():
        ''' select cbor_map() as m; '''
    assert {'m': b'\xa0'} == test()


def test_cbor_list():
    @sqlf.single_row
    @sqlf.sqlf
    def test():
        ''' select cbor_list() as m; '''
    assert {'m': b'\x80'} == test()


def test_cbor_map_insert():
    @sqlf.single_row
    @sqlf.sqlf
    def test():
        ''' select cbor_insert(cbor_map(), 'n', 3.14) as m; '''
    assert {'m': b'\xa1an\xfb@\t\x1e\xb8Q\xeb\x85\x1f'} == test()


def test_cbor_list_insert():
    @sqlf.single_row
    @sqlf.sqlf
    def test():
        ''' select cbor_insert(cbor_list(), 0, 3.14) as m; '''
    assert {'m': b'\x81\xfb@\t\x1e\xb8Q\xeb\x85\x1f'} == test()


def test_cbor_list_append():
    @sqlf.single_row
    @sqlf.sqlf
    def test():
        ''' select cbor_append(cbor_list(), 3.14) as m; '''
    assert {'m': b'\x81\xfb@\t\x1e\xb8Q\xeb\x85\x1f'} == test()


def test_cbor_has():
    @sqlf.single_row
    @sqlf.sqlf
    def test():
        ''' select cbor_has(cbor_insert(cbor_map(), 'n', 3.14), 'n') as m; '''
    assert {'m': 1} == test()


def test_cbor_get():
    @sqlf.single_row
    @sqlf.sqlf
    def test():
        ''' select cbor_get(cbor_insert(cbor_map(), 'n', 3.14), 'n') as m; '''
    assert {'m': 3.14} == test()
