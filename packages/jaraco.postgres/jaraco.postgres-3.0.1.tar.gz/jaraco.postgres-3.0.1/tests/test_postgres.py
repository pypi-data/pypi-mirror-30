# coding: utf-8

'''
Functional tests for the jaraco.postgres module.

Intended to be run using py.test.
'''

from __future__ import unicode_literals

import io
import os
import shutil
from subprocess import CalledProcessError

import psycopg2
import portend
import pytest

import jaraco.postgres as pgtools
from jaraco.postgres import PostgresDatabase, PostgresServer


HOST = os.environ.get('HOST', 'localhost')


class TestPostgresServer:
    def test_serves_postgres(self):
        port = portend.find_available_local_port()
        server = PostgresServer(HOST, port)
        server.initdb()

        try:
            server.start()
            version = server.get_version()

            assert len(version) > 0
            assert version[0] >= 8
        finally:
            server.destroy()

    def test_serves_postgres_with_locale(self):
        port = portend.find_available_local_port()
        server = PostgresServer(HOST, port)
        locale = 'C'
        server.initdb(locale=locale)

        try:
            server.start()
            server.get_version()  # To check we're able to talk to it.

            config = os.path.join(server.base_pathname, 'postgresql.conf')
            with io.open(config, encoding='utf-8') as strm:
                expect = "lc_messages = 'C'"
                assert any(expect in line for line in strm)
        finally:
            server.destroy()

    def test_unicode_value(self, monkeypatch):
        port = portend.find_available_local_port()
        monkeypatch.setitem(os.environ, 'LANG', 'C')
        server = PostgresServer(HOST, port)
        server.initdb()
        try:
            server.start()
            server.get_version()
            db = server.create('test_unicode')
            db.sql('CREATE TABLE records(name varchar(80))')
            db.sql("INSERT INTO records (name) VALUES (U&'\\2609')")
        finally:
            server.destroy()


class TestPostgresDatabase:
    def setup(self):
        self.port = portend.find_available_local_port()
        self.server = PostgresServer(HOST, self.port)
        self.server.initdb()
        self.server.start()

    def teardown(self):
        self.server.destroy()

    def test_creates_user_and_database(self):
        database = PostgresDatabase(
            'tests', user='john', host=HOST, port=self.port)

        database.create_user()
        database.create()

        rows = database.sql('SELECT 1')

        assert rows == [(1, )]


UNUSED_PORT = portend.find_available_local_port()


class Test_PostgresDatabase:
    @pytest.fixture(scope='class', autouse=True)
    def dbms(self, request):
        cls = request.cls
        cls.port = UNUSED_PORT
        cls.dbms = pgtools.PostgresServer(port=cls.port)
        cls.dbms.initdb()
        cls.dbms.start()
        yield
        cls.dbms.destroy()
        del cls.dbms

    @pytest.fixture(scope='function', autouse=True)
    def cleanup_database(self):
        yield
        if hasattr(self, 'database'):
            self.database.drop_if_exists()
            self.database.drop_user()

    def test___init__can_create_multiple_databases(self):
        database_1 = None
        database_2 = None
        try:
            database_1 = pgtools.PostgresDatabase(
                db_name='test_pgtools_1',
                port=self.port)
            database_2 = pgtools.PostgresDatabase(
                db_name='test_pgtools_2',
                port=self.port)
        finally:
            if database_1:
                database_1.drop_if_exists()
            if database_2:
                database_2.drop_if_exists()

    def test___init__ok(self):
        self.database = pgtools.PostgresDatabase(
            db_name='test_pgtools',
            port=self.port)

    def test___init__ok_when_port_integer(self):
        self.database = pgtools.PostgresDatabase(
            db_name='test_pgtools',
            port=int(self.port))

    def test___init__ok_when_port_string(self):
        self.database = pgtools.PostgresDatabase(
            db_name='test_pgtools',
            port=str(self.port))

    def test___repr__(self):
        self.database = pgtools.PostgresDatabase(
            db_name='test_pgtools',
            user='pmxtest', host='localhost', port=self.port,
            superuser='postgres', template='template1')
        assert repr(self.database) == (
            'PostgresDatabase(db_name=test_pgtools, user=pmxtest, '
            'host=localhost,'
            ' port=%s, superuser=postgres, template=template1)' % self.port
        )

    def test___str__(self):
        self.database = pgtools.PostgresDatabase(
            db_name='test_pgtools',
            user='pmxtest', host='localhost', port=self.port,
            superuser='postgres', template='template1')
        assert str(self.database) == (
            'PostgresDatabase(db_name=test_pgtools, user=pmxtest, '
            'host=localhost,'
            ' port=%s, superuser=postgres, template=template1)' % self.port
        )

    def test_create_fails_when_user_nonexistent(self):
        self.database = pgtools.PostgresDatabase(
            db_name='test_pgtools',
            port=self.port, user='no_such_user')
        with pytest.raises(CalledProcessError):
            self.database.create()

    def test_create_ok_when_no_sql(self):
        self.database = pgtools.PostgresDatabase(
            db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create()

    def test_create_ok_with_sql(self):
        self.database = pgtools.PostgresDatabase(
            db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create('CREATE TABLE test (value text)')

    def test_create_ok_with_sql_containing_unicode(self):
        self.database = pgtools.PostgresDatabase(
            db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create(
            'CREATE TABLE countries (value text) -- ¡México!')

    def test_create_ok_with_sql_using_psl_extensions(self):
        self.database = pgtools.PostgresDatabase(
            db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create('\set ON_ERROR_STOP FALSE\nSYNTAX ERROR HERE')

    def test_drop(self):
        self.database = pgtools.PostgresDatabase(
            db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create()
        self.database.drop()
        # Can't select; the database is gone!
        with pytest.raises(psycopg2.OperationalError):
            self.database.sql('SELECT 1')

    def test_drop_is_idempotent(self):
        self.database = pgtools.PostgresDatabase(
            db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create()
        self.database.drop()
        self.database.drop()
        self.database.drop()

    def test_psql_detects_bogus_params(self):
        self.database = pgtools.PostgresDatabase(
            db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create()

    def test_psql_detects_sql_error(self):
        self.database = pgtools.PostgresDatabase(
            db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create()
        with pytest.raises(CalledProcessError):
            self.database.psql(['-c', 'bogus'])

    def test_psql_ok_when_sql_is_valid(self):
        self.database = pgtools.PostgresDatabase(
            db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create()
        self.database.psql(['-c', 'SELECT 1'])

    def test_sql_detects_bogus_params(self):
        self.database = pgtools.PostgresDatabase(
            db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create()
        with pytest.raises(TypeError):
            self.database.sql(3.14)
        with pytest.raises(psycopg2.ProgrammingError):
            self.database.sql([])

    def test_sql_ok_when_sql_is_valid(self):
        self.database = pgtools.PostgresDatabase(
            db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create()
        assert self.database.sql('SELECT 1') == [(1,)]
        assert self.database.sql("SELECT 'hello', 2") == [('hello', 2)]

    def test_super_psql_detects_bogus_params(self):
        self.database = pgtools.PostgresDatabase(
            db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create()

    def test_super_psql_detects_sql_error(self):
        self.database = pgtools.PostgresDatabase(
            db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create()
        with pytest.raises(CalledProcessError):
            self.database.super_psql(['-c', 'bogus'])

    def test_super_psql_ok_when_sql_is_valid(self):
        self.database = pgtools.PostgresDatabase(
            db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create()
        self.database.super_psql(['-c', 'SELECT 1'])


class Test_PostgresServer:

    @pytest.fixture(autouse=True)
    def cleanup_dbms(self):
        yield
        if hasattr(self, 'dbms'):
            self.dbms.destroy()
            del self.dbms

    def test___init__ok(self):
        self.dbms = pgtools.PostgresServer(host='localhost', port=UNUSED_PORT)

    def test___repr__(self):
        self.dbms = pgtools.PostgresServer(host='localhost', port=UNUSED_PORT)
        assert repr(self.dbms) == (
            'PostgresServer(host=localhost, port=%s, '
            'base_pathname=%s, superuser=%s)'
            % (self.dbms.port, self.dbms.base_pathname, self.dbms.superuser)
        )

    def test___str__(self):
        self.dbms = pgtools.PostgresServer(host='localhost', port=UNUSED_PORT)
        assert str(self.dbms) == (
            'PostgreSQL server at %s:%s (with storage at %s)' %
            (self.dbms.host, self.dbms.port, self.dbms.base_pathname)
        )

    def test_destroy_handles_deleted_directory(self):
        self.dbms = pgtools.PostgresServer(host='localhost', port=UNUSED_PORT)
        self.dbms.initdb()
        # Reach under the covers and pre-emptively delete the directory.
        # (But first, some checking to prevent hideously
        # self-destructive acts.)
        assert self.dbms.base_pathname is not None
        assert self.dbms.base_pathname is not ''
        assert self.dbms.base_pathname is not '.'
        shutil.rmtree(self.dbms.base_pathname)
        self.dbms.destroy()

    def test_destroy_ok(self):
        self.dbms = pgtools.PostgresServer(host='localhost', port=UNUSED_PORT)
        self.dbms.destroy()

    def test_destroy_is_idempotent(self):
        self.dbms = pgtools.PostgresServer(host='localhost', port=UNUSED_PORT)
        self.dbms.destroy()
        self.dbms.destroy()
        self.dbms.destroy()

    def test_initdb_base_pathname_bogus(self):
        self.dbms = pgtools.PostgresServer(
            port=UNUSED_PORT, base_pathname='/n&^fX:d#f9')
        with pytest.raises((OSError, IOError)):
            self.dbms.initdb()

    def test_initdb_ok(self):
        self.dbms = pgtools.PostgresServer(port=UNUSED_PORT)
        self.dbms.initdb()

    def test_is_running(self):
        self.dbms = pgtools.PostgresServer(port=UNUSED_PORT)
        assert self.dbms.is_running() is False
        self.dbms.initdb()
        assert self.dbms.is_running() is False
        self.dbms.start()
        assert self.dbms.is_running() is True
        self.dbms.stop()
        assert self.dbms.is_running() is False

    def test_is_running_tries_bogus(self):
        self.dbms = pgtools.PostgresServer(port=UNUSED_PORT)
        self.dbms.initdb()
        with pytest.raises(ValueError):
            self.dbms.is_running(-1)
        with pytest.raises(ValueError):
            self.dbms.is_running(-10)
        with pytest.raises(ValueError):
            self.dbms.is_running(0)

    def test_pid(self):
        self.dbms = pgtools.PostgresServer(port=UNUSED_PORT)
        self.dbms.initdb()
        self.dbms.start()
        pid = self.dbms.pid

        # Weak test -- just check to see whether such a process exists.
        os.kill(pid, 0)
        self.dbms.stop()
        with pytest.raises(OSError):
            os.kill(pid, 0)

    def test_pid_returns_None_when_not_running(self):
        self.dbms = pgtools.PostgresServer(port=UNUSED_PORT)
        assert self.dbms.pid is None
        self.dbms.initdb()
        assert self.dbms.pid is None
        self.dbms.start()
        assert self.dbms.pid is not None
        os.kill(self.dbms.pid, 0)
        self.dbms.stop()
        assert self.dbms.pid is None

    def test_start_host_bogus(self):
        # Hostnames aren't checked until the postgres server starts up
        self.dbms = pgtools.PostgresServer(host='no.such.host.exists')
        self.dbms.initdb()
        with pytest.raises(RuntimeError):
            self.dbms.start()

    def test_start_port_out_of_range(self):
        self.dbms = pgtools.PostgresServer(port=99999999)
        self.dbms.initdb()
        errors = CalledProcessError, RuntimeError
        with pytest.raises(errors):
            self.dbms.start()

    def test_start_port_value_error(self):
        self.dbms = pgtools.PostgresServer(port='BOGUS')
        self.dbms.initdb()
        errors = CalledProcessError, RuntimeError
        with pytest.raises(errors):
            self.dbms.start()

    def test_start_ok(self):
        self.dbms = pgtools.PostgresServer(port=UNUSED_PORT)
        self.dbms.initdb()
        self.dbms.start()
        assert self.dbms.is_running() is True

    def test_start_raises_NotInitializedError_when_uninitialized(self):
        self.dbms = pgtools.PostgresServer(port=UNUSED_PORT)
        with pytest.raises(pgtools.NotInitializedError):
            self.dbms.start()

    def test_stop_is_idempotent(self):
        self.dbms = pgtools.PostgresServer(port=UNUSED_PORT)
        self.dbms.initdb()
        self.dbms.start()
        self.dbms.stop()
        self.dbms.stop()
        self.dbms.stop()
        assert self.dbms.is_running() is False

    def test_stop_ok(self):
        self.dbms = pgtools.PostgresServer(port=UNUSED_PORT)
        self.dbms.initdb()
        self.dbms.start()
        self.dbms.stop()
        assert self.dbms.is_running() is False
