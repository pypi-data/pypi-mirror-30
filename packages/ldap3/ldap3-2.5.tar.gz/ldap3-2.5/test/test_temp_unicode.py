# encoding: utf-8
from __future__ import unicode_literals
from ldap3 import get_config_parameter
import os
from ldap3.utils.conv import escape_filter_chars as eb
from ldap3 import Connection, Server
def test_search():
    print('ENCODING:', get_config_parameter('DEFAULT_CLIENT_ENCODING'))
    password = 'password'
    username = 'cn=admin,o=resources'
    root = 'o=test'
    hostname = 'ldap://edir1'
    server = Server(hostname)
    conn = Connection(
        server, user=username,
        password=password)
    conn.open()
    assert conn.bind()
    name = 'é'
    filter = '(cn=' + eb(name) + ')'
    conn.search(root, filter)

