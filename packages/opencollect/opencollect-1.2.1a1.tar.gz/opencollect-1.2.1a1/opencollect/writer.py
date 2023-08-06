# The MIT License (MIT)
#
# Copyright (c) 2018 James K Bowler, Data Centauri Ltd
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

#from openconnect.settings import HOST, USER, PASSWD
from threading import Thread
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb


class DatabaseWriter(Thread):
    """
    A class representing a threaded DatabaseWriter.
    It contains an id for tracking with the ability
    to handle different types of database sql statements

    Parameters
    ----------
    container  : NamedTuple
    
    """
    def __init__(self, container):
        super().__init__()
        self.id = container.identifer
        self._container = container
        #self._h = HOST
        #self._u = USER
        #self._p = PASSWD
        #self._con = self._db_connection()
        #self._cur = self._con.cursor()

    def _db_connection(self):
        return MySQLdb.connect(
                host=self._h,
                user=self._u,
                passwd=self._p
            )

    def _execute_many(self, stmt, payload):
        try:
            print(self.id, "stmt", "payload")
            #self._cur.executemany(stmt, payload)
            #self._con.commit()
        finally:
            #self._cur.close()
            #self._con.close()          
            pass

    def run(self):
        stmt = self._container.query
        payload = self._container.payload
        self._execute_many(stmt, payload)