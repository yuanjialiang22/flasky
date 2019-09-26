import configparser
import os

class ReadConfig:
    def __init__(self):
        configpath = os.path.join(os.getcwd(), 'config.ini')
        self.cf = configparser.ConfigParser()
        self.cf.read(configpath)

    def get_info(self, section, param):
        value = self.cf.get(section, param)
        return value

class getGlobalVars:
    def __init__(self):
        self.data = ReadConfig()

    def mysqlData(self):
        HOST     = self.data.get_info("Mysql-Database", "HOST")
        USER     = self.data.get_info("Mysql-Database", "USER")
        PASSWORD = self.data.get_info("Mysql-Database", "PWD")
        DB       = self.data.get_info("Mysql-Database", "DB")
        CHARSET  = self.data.get_info("Mysql-Database", "CHARSET")
        return HOST, USER, PASSWORD, DB, CHARSET

    def emailData(self):
        MAIL_SERVER  = self.data.get_info("Email", "MAIL_SERVER")
        MAIL_PORT    = self.data.get_info("Email", "MAIL_PORT")
        MAIL_ADDRESS = self.data.get_info("Email", "MAIL_ADDRESS")
        MAIL_PWD     = self.data.get_info("Email", "MAIL_PWD")
        ADMIN_EMAIL  = self.data.get_info("Email", "MAIL_SEND_USER")
        return MAIL_SERVER, MAIL_PORT, MAIL_ADDRESS, MAIL_PWD, ADMIN_EMAIL
