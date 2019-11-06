import pymysql

class Mysql_Utils():
    def __init__(self, host, port, user, pwd, dbname):
        self.__conn = None
        self.__cursor = None
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.dbname = dbname

    def __init_conn(self):
        try:
            conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.pwd, db=self.dbname)
        except pymysql.Error as e:
            raise ConnectionError(e)
        self.__conn = conn

    def __init_cursor(self):
        if self.__conn:
            self.__cursor = self.__conn.cursor(pymysql.cursors.DictCursor)

    def close(self):
        if self.__conn:
            self.__conn.close()
            self.__conn = None

    def exec_sql(self, sql, args=None):
        try:
            if self.__conn is None:
                self.__init_conn()
                self.__init_cursor()
            self.__cursor.execute(sql, args)
            results = self.__cursor.fetchall()
            return results
        except pymysql.Error as e:
            raise pymysql.Error(e)
        finally:
            if self.__conn:
                self.close()

    def exec_txsql(self, sql, args=None):
        try:
            if self.__conn is None:
                self.__init_conn()
                self.__init_cursor()
            if self.__cursor is None:
                self.__init_cursor()
            self.rows_affected = self.__cursor.execute(sql, args)
            return self.rows_affected
        except pymysql.Error as e:
            raise pymysql.Error(e)
        finally:
            if self.__cursor:
                self.__cursor.close()
                self.__cursor = None

    def commit(self):
        try:
            if self.__conn:
                self.__conn.commit()
        except pymysql.Error as e:
            raise pymysql.Error(e)
        finally:
            if self.__conn:
                self.close()