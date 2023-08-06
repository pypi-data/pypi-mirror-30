#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sqlf` package."""

# import pytest
import sqlf


###############################################################################
# sqlf.sql with DELETE
###############################################################################


def test_delete_one_row():
    @sqlf.sqlf
    def test():
        ''' create table test_table (a, b);
            insert into test_table values (1, 2);
            insert into test_table values (2, 3);
            delete from test_table where a=2;
            select * from test_table;
            drop table test_table;
        '''
    tmp = list(test())
    assert len(tmp) == 1
    assert {'a': 1, 'b': 2} in tmp
