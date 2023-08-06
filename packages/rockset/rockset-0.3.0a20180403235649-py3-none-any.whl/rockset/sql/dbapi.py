"""DB-API implementation backed by Rockset

See http://www.python.org/dev/peps/pep-0249/

TODO:
- Handle DATE, TIME, INTERVAL (etc) data types
- Do not bind parameters in query in Cursor.execute*.
  Pass it along without any escaping shenanigans.

"""
from rockset import Client
from rockset.sql.exception import *
import rockset

import collections

#
# Global constants
#
# supported DBAPI level
apilevel = '2.0'
# Python extended format codes, e.g. ...WHERE name=%(name)s
paramstyle = 'pyformat'
# Threads may share the module and connections.
threadsafety = 2


def connect(*args, **kwargs):
    """Constructor for creating a connection to Rockset. Any argument that you
    pass to create a Rockset Client_ can be passed here.

    :returns: a :py:class:`Connection` object.
    """
    return Connection(*args, **kwargs)


class Connection(object):
    """Setup a Rockset Client handle
    """

    def __init__(self, *args, **kwargs):
        try:
            self._client = Client(*args, **kwargs)
            self._client.list()
        except rockset.exception.Error as e:
            raise Error.from_rockset_exception(e)

    def close(self):
        pass

    def commit(self):
        pass

    def rollback(self):
        raise NotSupportedError("Rockset does not support transactions")

    def cursor(self, cursor_type=None):
        if cursor_type is None:
            cursor_type = Cursor
        elif not issubclass(cursor_type, Cursor):
            raise ValueError('{} is not a valid cursor type'.format(cursor_type))
        return cursor_type(conn=self, client=self._client)


class Cursor(object):
    """These objects represent a database cursor, which is used to manage the
    context of a fetch operation. Cursors created from the same connection are
    not isolated, i.e., any changes done to the database by a cursor are
    immediately visible by the other cursors.
    """
    def __init__(self, conn, client):
        """DBAPI Cursor
        """
        self._conn = conn
        self._client = client
        self._cursor = None
        self._cursor_iter = None
        self._arraysize = 1

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    @property
    def description(self):
        """This read-only attribute is a sequence of 7-item sequences.

        Each of these sequences contains information describing one result
        column:
            name
            type_code
            display_size (optional, always None for now)
            internal_size (optional, always None for now)
            precision (optional, always None for now)
            scale (optional, always None for now)
            null_ok (optional, always True for now)

        The first two items (name and type_code) are mandatory, the other
        five are optional and are set to None if no meaningful values can be
        provided.

        This attribute will be None for operations that do not return rows or
        if the cursor has not had an operation invoked via the .execute*()
        method yet.

        The type_code can be interpreted by comparing it to the Type Objects
        specified in the section below.
        """
        if self._cursor is None:
            return None

        # get first record and show columns from there
        try:
            results = self._cursor.results()
        except rockset.exception.Error as e:
            raise Error.from_rockset_exception(e)

        row = {}
        if len(results) > 0:
            row = results[0]

        return [
            # name, type_code, display_size, internal_size, precision, scale,
            # null_ok
            (k, type(v).__name__, None, None, None, None, (k != ':id'))
                for k,v in row.items()
        ]

    @property
    def rowcount(self):
        return -1

    def close(self):
        """Close the cursor now (rather than whenever __del__ is called).

        The cursor will be unusable from this point forward; an Error (or
        subclass) exception will be raised if any operation is attempted with
        the cursor.
        """
        self._cursor = None
        self._cursor_iter = None

    def execute(self, operation, parameters=None):
        """Prepare and execute a database operation (query or command).
        Parameters may be provided as sequence or mapping and will be bound to
        variables in the operation. Variables are specified in ``pyformat``
        notation.

        Return values are not defined.
        """
        if parameters is None:
            sql = operation
        else:
            escaper = _ParamEscaper()
            sql = operation % escaper.escape_args(parameters)
        # setup the cursor
        self._cursor = self._client.sql(sql=operation)
        # setup an iterator to fetch results
        self._cursor_iter = self._cursor.iter(batch=None)

    def executemany(operation, seq_of_parameters):
        """Prepare a database operation (query or command) and then execute it
        against all parameter sequences or mappings found in the sequence
        ``seq_of_parameters``.

        Only the final result set is retained.

        Return values are not defined.
        """
        for parameters in seq_of_parameters[:-1]:
            self.execute(operation, parameters)
        if seq_of_parameters:
            self.execute(operation, seq_of_parameters[-1])

    def _fetchonedoc(self):
        if self._cursor is None:
            raise ProgrammingError(message='no query has been executed yet')
        try:
            one = next(self._cursor_iter)
        except StopIteration:
            return None
        except rockset.exception.Error as e:
            raise Error.from_rockset_exception(e)
        return one

    def fetchone(self):
        """Fetch the next row of a query result set, returning a single
        sequence, or None when no more data is available.

        An Error (or subclass) exception is raised if the previous call to
        .execute*() did not produce any result set or no call was issued yet.
        """
        one = self._fetchonedoc()
        if one is None:
            return None
        return tuple(one.values())

    def fetchmany(self, size=None):
        """Fetch the next set of rows of a query result, returning a sequence
        of sequences (e.g. a list of tuples). An empty sequence is returned
        when no more rows are available.

        The number of rows to fetch per call is specified by the parameter. If
        it is not given, the cursor's arraysize determines the number of rows
        to be fetched. The method should try to fetch as many rows as indicated
        by the size parameter. If this is not possible due to the
        specified number of rows not being available, fewer rows may be
        returned.

        An Error (or subclass) exception is raised if the previous call to
        .execute*() did not produce any result set or no call was issued yet.
        """
        if size is None:
            size = self.arraysize
        result = []
        for _ in range(size):
            one = self.fetchone()
            if one is None:
                break
            else:
                result.append(one)
        return result

    def fetchall(self):
        """Fetch all (remaining) rows of a query result, returning them as a
        sequence of sequences (e.g. a list of tuples).

        An Error (or subclass) exception is raised if the previous call to
        .execute*() did not produce any result set or no call was issued yet.
        """
        result = []
        while True:
            one = self.fetchone()
            if one is None:
                break
            else:
                result.append(one)
        return result

    @property
    def arraysize(self):
        """This read/write attribute specifies the number of rows to fetch at a
        time with .fetchmany(). It defaults to 1 meaning to fetch a single row
        at a time.
        """
        return self._arraysize

    @arraysize.setter
    def arraysize(self, value):
        self._arraysize = value

    def setinputsizes(self, sizes):
        pass

    def setoutputsize(self, size, column=None):
        pass

    # Optional DB-API Extensions
    @property
    def connection(self):
        return self._conn

    def __next__(self):
        """Return the next row from the currently executing SQL statement using
        the same semantics as .fetchone(). A ``StopIteration`` exception is
        raised when the result set is exhausted.
        """
        one = self.fetchone()
        if one is None:
            raise StopIteration
        else:
            return one

    next = __next__

    def __iter__(self):
        """Return self to make cursors compatible to the iteration protocol."""
        return self

class DictCursor(Cursor):
    def fetchone(self):
        return self._fetchonedoc()


class _ParamEscaper(object):
    def escape_args(self, parameters):
        if isinstance(parameters, dict):
            return {k: self.escape_item(v) for k, v in parameters.items()}
        elif isinstance(parameters, (list, tuple)):
            return tuple(self.escape_item(x) for x in parameters)
        else:
            raise ProgrammingError("Unsupported param format: {}".format(
                parameters))

    def escape_number(self, item):
        return item

    def escape_string(self, item):
        """Need to decode UTF-8 because of old sqlalchemy.
        Newer SQLAlchemy checks dialect.supports_unicode_binds before encoding
        Unicode strings as byte strings. The old version always encodes Unicode
        as byte strings, which breaks string formatting here.
        """
        if isinstance(item, bytes):
            item = item.decode('utf-8')
        """This is good enough when backslashes are literal, newlines are just
        followed, and the way to escape a single quote is to put two single
        quotes.  (i.e. only special character is single quote)
        """
        return "'{}'".format(item.replace("'", "''"))

    def escape_sequence(self, item):
        l = map(str, map(self.escape_item, item))
        return '(' + ','.join(l) + ')'

    def escape_item(self, item):
        if item is None:
            return 'NULL'
        elif isinstance(item, (int, float)):
            return self.escape_number(item)
        elif isinstance(item, str):
            return self.escape_string(item)
        elif isinstance(item, collections.Iterable):
            return self.escape_sequence(item)
        else:
            raise ProgrammingError("Unsupported object {}".format(item))

#
# Type Objects
# See https://www.python.org/dev/peps/pep-0249/#implementation-hints-for-module-authors
#
class _DBAPITypeObject:
    def __init__(self, *values):
        self.values = values

    def __cmp__(self, other):
        if other in self.values:
            return 0
        if other < self.values:
            return 1
        else:
            return -1

Binary = str
STRING = _DBAPITypeObject(['str'])
BINARY = _DBAPITypeObject()
NUMBER = _DBAPITypeObject(['int', 'float'])
DATETIME = _DBAPITypeObject()
ROWID = _DBAPITypeObject()
BOOL = _DBAPITypeObject(['bool'])
JSON = _DBAPITypeObject(['dict'])
ARRAY = _DBAPITypeObject(['list'])


