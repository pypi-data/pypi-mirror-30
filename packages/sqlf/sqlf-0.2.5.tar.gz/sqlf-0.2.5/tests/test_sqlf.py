#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `sqlf` package."""

import pytest
import sqlf

################################################################################
# Old API (sqlfunc)
################################################################################

db = sqlf.sqldb('''
    CREATE TABLE IF NOT EXISTS users (
        userid   INTEGER PRIMARY KEY,
        username TEXT    UNIQUE NOT NULL,
        bcrypt   BLOB    NOT NULL
    );
''', database=':memory:') # this is the default

@db.sqludf
def bcrypt_hash(password):
    # call to library here
    return b'$2b$12$.OjbRwRejxw92C89sA6JkOVrhmQzGsjoyCf1ofIN9hUNdHFufb3ty'

@db.sqludf
def bcrypt_verify(password, bcrypthash):
    # call to library here
    return 'password123' == password

@db.sqlfunc
def add_user(username, password):
    ''' INSERT OR IGNORE INTO users (username, bcrypt)
        VALUES (:username, bcrypt_hash(:password));
    '''

@db.sqlfunc(post=bool, single=True, default=False)
def login(username, password):
    ''' SELECT 1 FROM users
        WHERE username=:username
          AND bcrypt_verify(:password, bcrypt);
    '''

@db.sqlfunc
def list_users():
    ''' SELECT userid, username FROM users;
    '''

def test_scenario():
    '''Test script ported from sqlfunc'''

    add_user('root', 'password123')

    x1 = login('root', 'secret')
    print('x1', x1)
    assert False == x1

    x2 = login('root', 'password123')
    print('x2', x2)
    assert True == x2

    x3 = list_users()
    print('x3', x3)
    assert len(x3) == 1

################################################################################
# New API (sqlf)
################################################################################

def test_new():
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
