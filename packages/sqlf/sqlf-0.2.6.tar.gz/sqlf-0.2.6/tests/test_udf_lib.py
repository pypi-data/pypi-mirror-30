#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sqlf` package."""

import sqlf.udf_lib


################################################################################
# Text Processing
################################################################################

def test_match():
    assert sqlf.udf_lib.match('this is a test', ' this is a test')
    assert sqlf.udf_lib.match('This is a Test', 'this IS  a test')
    assert sqlf.udf_lib.match('This-is-a-Test', 'this_is.a.test')

def test_number():
    assert 8 == sqlf.udf_lib.number('8 deg')
    assert 8.5 == sqlf.udf_lib.number('@ 8.5 eur')
    assert None == sqlf.udf_lib.number('@ _ eur')
