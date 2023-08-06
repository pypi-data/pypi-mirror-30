#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sqlf` package."""

import pytest
import sqlf


###############################################################################
# Data Cryptography UDFs
###############################################################################


@pytest.mark.parametrize("length", [0, 1, 20, 30, 40, 500])
def test_nonce(length):
    @sqlf.single_row
    @sqlf.sqlf
    def test(length):
        ''' select nonce(:length) as nonce; '''
    tmp = test(length)
    assert isinstance(tmp['nonce'], bytes)
    assert len(tmp['nonce']) == length


def test_sha3():
    @sqlf.single_row
    @sqlf.sqlf
    def test(txt1, txt2):
        ''' select sha3(:txt1) = sha3(:txt2) as res,
                   length(sha3(:txt1)) as length;
        '''
    assert {'res': True, 'length': 64} == test('same', 'same')
    assert {'res': False, 'length': 64} == test('not', 'same')
