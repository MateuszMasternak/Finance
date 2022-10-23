import os, sqlite3
from dotenv import load_dotenv


class Database:
    def __init__(self, db_name):
        self.con = sqlite3.connect(db_name, check_same_thread=False)
        self.cur = self.con.cursor()
        
    def __del__(self):
        self.con.close()
