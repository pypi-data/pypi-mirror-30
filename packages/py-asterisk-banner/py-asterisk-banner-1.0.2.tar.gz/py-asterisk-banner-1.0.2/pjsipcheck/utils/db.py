from pjsipcheck import settings

import logging
import sqlite3
import os.path


class DB:
    """ Connection and operate with sqlite3 database """
    dbfile = settings.CONFIG.get_database('file')

    def __init__(self):
        """ Constructor of the class where we set where to save db file """
        self.log = logging.getLogger(settings.LOGGER_NAME)
        self.log.debug("DataBase object created")

    def init_db(self):
        """ Init database """

        self.log.debug("Usando el archivo sqlite %s" % self.dbfile)

        if self.exists() is not True:
            self.log.debug("Creando archivo de base de datos %s " % self.dbfile)
            self.create_table()

        if self.check() is not True:
            self.log.error("No se pudo crear el archivo %s" % self.dbfile)
            return False

        return True

    def exists(self):
        """  Verify if file exists """
        return os.path.isfile(self.dbfile)

    def check(self):
        """  Is writable, is a valid sqlite3 file and contains all necessary tables """
        if self.exists() is not True:
            self.log.debug("DataBase doesn't exist")
            return False
        if os.access(self.dbfile, os.R_OK) is not True:
            self.log.debug("DataBase isn't readable")
            return False
        if os.access(self.dbfile, os.W_OK) is not True:
            self.log.debug("DataBase isn't writable")
            return False
        return True

    def sql(self, sql, params=()):
        """ Method to connect and execute some SQL sentence """
        conn = None
        data = None
        try:
            conn = sqlite3.connect(self.dbfile)
            cur = conn.cursor()
            cur.execute(sql, params)
            conn.commit()
            data = cur.fetchall()
        except sqlite3.Error as error:
            self.log.debug("Error in sql => %s" % error)
        finally:
            if conn is not None:
                conn.close()
        return data

    def create_table(self):
        """ Creation of table structure """
        self.log.debug("Creating table")
        return self.sql("""CREATE TABLE banned
                        (ip,
                        try DEFAULT 0,
                        block DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        )""")

    def show_ips(self):
        """ Return IPS in banned table """
        return self.sql("""SELECT ip, try, block, created_at, updated_at FROM banned""")

    def show_blocked(self):
        """ Return IP blocked from banned table """
        blocks = self.sql("SELECT ip FROM banned WHERE block = 1")
        response = []
        for block in blocks:
            response.append(block[0])
        return response

    def check_bannedip(self, ipaddress):
        """ Method to check if ip is into the table of banned ips """
        self.log.debug("Comprobando IP %s" % ipaddress)
        existe = self.sql("SELECT try FROM banned WHERE ip = ?", (ipaddress,))
        return existe

    def insert_ip(self, ipaddress, ntry=1):
        """ Method to insert IP into the table of banned ips """
        tries = 1
        existe = self.check_bannedip(ipaddress)
        if len(existe) is 0:
            self.log.debug("Insertando IP %s" % ipaddress)
            self.sql("INSERT INTO banned (ip) VALUES (?)", (ipaddress,))
        else:
            self.log.debug("Actualizando intentos IP %s" % ipaddress)
            tries = int(existe[0][0]) + ntry
            self.sql("""UPDATE banned SET
                        updated_at=DATETIME('now'), try=? WHERE ip=?""", (tries, ipaddress,))
        return tries

    def block_ip(self, ipaddress):
        """ Block IP address """
        done = False
        self.insert_ip(ipaddress, 0)
        res = self.sql("""UPDATE banned
                        SET updated_at=DATETIME('now'), block = 1
                        WHERE ip=?""", (ipaddress,))
        if res is not None:
            self.log.debug("Bloqueo IP %s" % ipaddress)
            done = True
        return done

    def unblock_ip(self, ipaddress):
        """ Unblock IP address """
        done = False
        self.insert_ip(ipaddress, 0)
        res = self.sql("""UPDATE banned
            SET updated_at=DATETIME('now'), block = 0 WHERE ip=?""",
                       (ipaddress,))
        if res is not None:
            self.log.debug("Desbloqueo IP %s" % ipaddress)
            done = True
        return done

    def delete_ip(self, ipaddress):
        """ Delete IP from the table """
        done = False
        self.insert_ip(ipaddress, 0)
        res = self.sql("DELETE FROM banned WHERE ip=?", (ipaddress,))
        if res is not None:
            self.log.debug("Borrada IP %s" % ipaddress)
            done = True
        return done
