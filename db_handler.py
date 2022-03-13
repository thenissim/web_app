# -------------------------------------------------------------------------------
# DbHandler
# -------------------------------------------------------------------------------
# A class to interact with the database
#-------------------------------------------------------------------------
# Author       - Adar Nissim, Eden Lotan, Tamar Holder      
# Last updated - 09.01.2021
#-------------------------------------------------------------------------


# import logging so we can write messages to the log
import logging
import os
#import DB library
import MySQLdb


# Database connection parameters 
DB_USER_NAME='db_team26'
DB_PASSWORD='gimfzclf'
DB_DEFALUT_DB='db_team26'

class DbHandler():
    def __init__(self):
        self.m_user=DB_USER_NAME
        self.m_password=DB_PASSWORD
        self.m_default_db=DB_DEFALUT_DB
        self.m_charset='utf8'
        self.m_host='34.122.221.36'
        self.m_port=3306
        self.m_DbConnection=None

    def connectToDb(self):
        # we will connect to the DB only once
        if self.m_DbConnection is None:
            # connect to the DB
            self.m_DbConnection = MySQLdb.connect(
            host=self.m_host,
            db=self.m_default_db,
            port=self.m_port,
            user= self.m_user,
            passwd=self.m_password,
            charset=self.m_charset)

    def disconnectFromDb(self):
        if self.m_DbConnection:
            self.m_DbConnection.close()
            
    def commit(self):
        if self.m_DbConnection:
            self.m_DbConnection.commit()
            
    def getCursor(self):
        self.connectToDb()
        return (self.m_DbConnection.cursor())