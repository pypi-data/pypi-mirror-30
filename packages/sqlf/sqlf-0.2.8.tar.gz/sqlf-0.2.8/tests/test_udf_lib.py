#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sqlf` package."""

import sqlf.udf_lib


###############################################################################
# Text Processing
###############################################################################


def test_similar():
    assert sqlf.udf_lib.similar('this is a test', ' this is a test')
    assert sqlf.udf_lib.similar('This is a Test', 'this IS  a test')
    assert sqlf.udf_lib.similar('This-is-a-Test', 'this_is.a.test')


def test_number():
    assert 8 == sqlf.udf_lib.number('8 deg')
    assert 8.5 == sqlf.udf_lib.number('@ 8.5 eur')
    assert sqlf.udf_lib.number('@ _ eur') is None


###############################################################################
# Data Encodings
###############################################################################


def test_tohex():
    assert sqlf.udf_lib.tohex(b'test') == '74657374'


###############################################################################
# Data Serialisation
###############################################################################


def test_cbor():
    tmp = dict(name='herby', pi=3.14, lst=[1, 2], dct=dict())
    assert sqlf.udf_lib.uncbor(sqlf.udf_lib.cbor(tmp)) == tmp


###############################################################################
# Cryptography
###############################################################################


def test_nonce():
    assert len(sqlf.udf_lib.nonce(22)) == 22


def test_cryptography_sha3():
    assert sqlf.udf_lib.sha3('test')
    assert sqlf.udf_lib.sha3(b'test')
    assert len(sqlf.udf_lib.sha3('a')) == len(sqlf.udf_lib.sha3('aaaaaaaa'))
