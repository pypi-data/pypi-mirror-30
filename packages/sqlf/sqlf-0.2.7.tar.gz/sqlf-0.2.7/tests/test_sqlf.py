#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sqlf` package."""

# import pytest
import sqlf


################################################################################
# New API (sqlf)
################################################################################

def test_old_scenario():
    '''Test script ported from sqlfunc'''

    @sqlf.sql()
    def setup():
        '''
            CREATE TABLE IF NOT EXISTS users (
                userid   INTEGER PRIMARY KEY,
                username TEXT    UNIQUE NOT NULL,
                bcrypt   BLOB    NOT NULL
            );
        '''

    @sqlf.scalar_udf
    def bcrypt_hash(password):
        return b'$2b$12$.OjbRwRejxw92C89sA6JkOVrhmQzGsjoyCf1ofIN9hUNdHFufb3ty'

    @sqlf.scalar_udf
    def bcrypt_verify(password, bcrypthash):
        return 'password123' == password

    @sqlf.sql()
    def add_user(username, password):
        ''' INSERT OR IGNORE INTO users (username, bcrypt)
            VALUES (:username, bcrypt_hash(:password));
        '''

    @sqlf.sql()
    def login(username, password):
        ''' SELECT 1 FROM users
            WHERE username=:username
              AND bcrypt_verify(:password, bcrypt);
        '''

    @sqlf.sql()
    def list_users():
        ''' SELECT userid, username FROM users;
        '''

    x0 = list(setup())
    assert len(x0) == 0

    x1 = list(add_user('root', 'password123'))
    assert len(x1) == 0

    x2 = list(login('root', 'secret'))
    assert len(x2) == 0

    x3 = list(login('root', 'password123'))
    assert len(x3) == 1

    x4 = list(list_users())
    assert len(x4) == 1


def test_new_scenario():
    @sqlf.sql()
    def _setup():
        ''' create table tests (a, b, c, d); '''

    @sqlf.sql()
    def _insert(a, b=2, c=3):
        ''' insert into tests (a, b, c, d) values (:a, :b, :c, :c); '''

    @sqlf.sql()
    def _query():
        ''' select * from tests; '''

    assert 0 == len(list(_setup()))
    assert 0 == len(list(_query()))
    assert 0 == len(list(_insert(1, b=3)))
    assert 1 == len(list(_query()))


def test_scalar_udf():
    @sqlf.scalar_udf
    def one():
        return 1
    @sqlf.sql()
    def _select_one():
        ''' select one() as one; '''
    assert [{'one': 1}] == list(_select_one())
