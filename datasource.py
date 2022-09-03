from tkinter.messagebox import NO
import psycopg2
import logging
from psycopg2.errors import UniqueViolation

logger = logging.getLogger()
GET_ALL_USERNAMES = "SELECT * FROM usernames"
DELETE_USERNAME = "DELETE FROM usernames WHERE username = %s"
INSERT_USERNAME = "INSERT INTO usernames VALUES(%s)"
FIND_USERNAME = "SELECT * FROM usernames WHERE username = %s"

class Datasource:
    def __init__(self,databse_url):
        self.databse_url = databse_url
    
    def get_connection(self):
        return psycopg2.connect(self.databse_url,sslmode = "allow")
    
    @staticmethod
    def close_connection(conn):
        if conn is not None:
            conn.close()
    
    def createTables(self):
        Commands = (
            """
            CREATE TABLE IF NOT EXISTS usernames(
                username varchar(5000) PRIMARY KEY
            )
            """,
        )

        conn = None
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            for command in Commands:
                print(command)
                cur.execute(command)
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise error
        finally:
            self.close_connection(conn)
        
    def getAllUsernames(self):
        conn = None
        data= None
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(GET_ALL_USERNAMES)
            data = cur.fetchall()
            cur.close()
            conn.commit()
            return data
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise error
        finally:
            self.close_connection(conn)
    
    def deleteUsername(self,username):
        conn = None
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(DELETE_USERNAME,(username,))
            cur.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise error
        finally:
            self.close_connection(conn)
    
    def addUsername(self,username,update):
        conn = None
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(INSERT_USERNAME,(username,))
            cur.close()
            conn.commit()
            return True
        except UniqueViolation:
            update.message.reply_text("This username/id already exists")
            return False
        except (Exception, psycopg2.DatabaseError) as error:
            print(type(error))
            logger.error(error)
            raise error
        finally:
            self.close_connection(conn)
    
    def checkIfUserExists(self,username):
        conn = None
        exists = True
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(FIND_USERNAME,(username,))
            if(len(cur.fetchall())==0):
                exists = False
            
            cur.close()
            conn.commit()
            return exists
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            
        finally:
            self.close_connection(conn)
    

