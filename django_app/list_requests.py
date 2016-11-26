from __future__ import print_function
from __future__ import unicode_literals

import cx_Oracle
from django.db import connections
from utils import _get_row_names, execute_function
from registraton_authorization import login
from registraton_authorization import get_current_connection
from errors import AccessDeniedError


def list_request(request, function_name, args=list()):
    #print(dir(connection.cursor().db.connection.username))
    #print(connection.cursor().db.connect())
    # print(dir(connection.connect))
    # login('kagura', 'passwordlsnrctl stat ')
    if request.COOKIES. has_key('connection'):
        current_connection = request.COOKIES['connection']
    else:
        current_connection = 'default'

    try:
        cursor = connections[current_connection].cursor()
        # print(connections[current_connection].connection.username)
        client_cursor = cursor.callfunc(execute_function(function_name), cx_Oracle.CURSOR, args)

        data = client_cursor.fetchall()
        # print(len(data))
        row_names = _get_row_names(client_cursor.description)

        return row_names, data
    except cx_Oracle.DatabaseError:
        raise AccessDeniedError()
