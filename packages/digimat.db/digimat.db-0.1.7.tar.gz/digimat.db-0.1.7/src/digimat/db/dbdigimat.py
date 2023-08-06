# brew install mysql-connector-c
# import MySQLdb
import pymysql as mysql

# from contextlib import closing
# from warnings import filterwarnings

from datetime import datetime
# from datetime import timedelta

# DB Backup
# mysqldump -u root -p xxx --routines --no-data digimat > digimat-schema.sql


class DBDigimat(object):
    def __init__(self, host, user, password, ssl, logger):
        self._host=host
        self._user=user
        self._password=password
        self._database='digimat'
        self._ssl=ssl
        self._mysql=None

        self._logger=logger
        self.onInit()

    def onInit(self):
        pass

    @property
    def logger(self):
        return self._logger

    @property
    def mysql(self):
        return self._mysql

    def ignoreWarnings(self):
        print('TODO: Filterwarnings')
        # filterwarnings('ignore', category=MySQLdb.Warning)

    def setDatabase(self, database):
        self._database=database

    def connect(self):
        if self._mysql is not None:
            return self._mysql

        self.logger.info("mysql(%s):connecting as [%s]..." % (self._host, self._user))
        self._mysql=None
        try:
            self._mysql=mysql.connect(host=self._host,
                user=self._user,
                passwd=self._password,
                db=self._database,
                connect_timeout=10, compress=False,
                ssl=self._ssl)

            # important, every UPDATE/INSERT/DELETE order must be commited with mysqlCommit()!
            self._mysql.autocommit(False)
        except:
            self.logger.exception("connect() error!")

        return self._mysql

    def cursorArray(self):
        try:
            return self.connect().cursor()
        except:
            self.logger.exception("cursorArray() error!")

    def cursor(self):
        return self.cursorArray()

    def cursorDict(self):
        try:
            return self.connect().cursor(mysql.cursors.DictCursor)
        except:
            self.logger.exception("cursorDict() error!")

    def commit(self):
        try:
            self._mysql.commit()
            return True
        except:
            self.logger.exception("commit error!")

    def rollback(self):
        try:
            self._mysql.rollback()
            return True
        except:
            self.logger.exception("rollback error!")

    def closeCursor(self, cursor):
        try:
            if cursor:
                cursor.close()
        except:
            pass

    def execute(self, cursor, sql, args=None):
        rowsAffected=None
        if cursor:
            try:
                # print "[SQL:%s]" % sql
                rowsAffected=cursor.execute(sql, args)
                # print "[SQL-QUERY-ROWCOUNT=%d]" % c.rowcount
                # don't forget to close the cursor once used!
                # don't forget to commit the transaction once terminated (for INSERT, UPDATE, DELETE)
                # print "AFFECTED:", rowsAffected
                return rowsAffected
            except mysql.Error as e:
                try:
                    self.logger.error("mysql(%s):error [%d]: %s" % (self._host, e.args[0], e.args[1]))
                except IndexError:
                    self.logger.error("mysql(%s):error: %s" % (self._host, str(e)))

    def executeMany(self, cursor, sql, args=None):
        rowsAffected=None
        if cursor:
            try:
                # print "[M-SQL:%s]" % sql
                rowsAffected=cursor.executemany(sql, args)
                # print "[SQL-QUERY-ROWCOUNT=%d]" % c.rowcount
                # don't forget to close the cursor once used!
                # don't forget to commit the transaction once terminated (for INSERT, UPDATE, DELETE)
                # print "AFFECTED:", rowsAffected
                return rowsAffected
            except mysql.Error as e:
                try:
                    self.logger.error("mysql(%s):error [%d]: %s" % (self._host, e.args[0], e.args[1]))
                except IndexError:
                    self.logger.error("mysql(%s):error: %s" % (self._host, str(e)))

    def optimizeTable(self, table):
        sql="OPTIMIZE TABLE `%s`" % table

        cursor=self.cursor()
        result=self.execute(cursor, sql) is not None
        cursor.close()
        if self.commit():
            return result

    def fetchall(self, cursor, sql, args=None):
        if self.execute(cursor, sql, args) is not None:
            try:
                rows=cursor.fetchall()
            except:
                rows=None
                self.logger.error("mysql(%s):fetchall error (%s)!" % (self._host, sql))
            return rows

    def fetch1(self, cursor, sql, args=None):
        try:
            return self.fetchall(cursor, sql, args)[0]
        except:
            pass

    def fetchArray(self, sql, args=None):
        cursor=self.cursorArray()
        data=self.fetchall(cursor, sql, args)
        cursor.close()
        return data

    def fetchArray1(self, sql, args=None):
        try:
            return self.fetchArray(sql, args)[0]
        except:
            pass

    def fetchDict(self, sql, args=None):
        cursor=self.cursorDict()
        data=self.fetchall(cursor, sql, args)
        cursor.close()
        return data

    def fetchDict1(self, sql, args=None):
        try:
            return self.fetchDict(sql, args)[0]
        except:
            self.logger.exception("mysql(%s):fetchDict1(%s)" % (self._host, sql))
            pass

    def fetchField(self, sql, field, args=None):
        try:
            return self.fetchDict1(sql, args)[field]
        except:
            self.logger.exception("mysql(%s):fetchField(%s)" % (self._host, field))
            pass

    def disconnect(self):
        try:
            if self._mysql:
                self.logger.info("mysql(%s):disconnect" % self._host)
            self._mysql.close()
        except:
            pass
        self._mysql=None

    def close(self):
        self.disconnect()

    def now(self, delta=None):
        dt=datetime.now()
        if delta is not None:
            dt+=delta
        return dt

    def stamp(self, dt=None):
        if dt is None:
            dt=self.now()
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def stampDate(self, dt=None):
        if dt is None:
            dt=self.now()
        return dt.strftime('%Y-%m-%d')


class DBRecords(object):
    def __init__(self, dbi):
        self._db=dbi

    @property
    def db(self):
        return self._db

    def retrieve(self, key, dtFrom=None, dtTo=None):
        sql="""
            SELECT *
            FROM `records`
            INNER JOIN `keys` ON `keys`.id=records.idkey
            WHERE `keys`.`key`='%s'
            """ % key
        if dtFrom:
            sql+=" AND `record.stamp`>='%s'" % self.db.stamp(dtFrom)
        if dtTo:
            sql+=" AND `records.stamp`<='%s'" % self.db.stamp(dtTo)

        cursor=self.db.cursor()

        rows=None
        if cursor:
            rows=self.db.fetchall(cursor, sql)
            cursor.close()
        return rows


if __name__ == '__main__':
    pass
