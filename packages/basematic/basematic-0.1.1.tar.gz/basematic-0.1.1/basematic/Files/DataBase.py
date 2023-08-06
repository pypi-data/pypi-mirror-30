import sqlite3
import os
from sqlalchemy import *
from basematic.Files.Folder import MakesurePath

class ModuleDatas:
    def __init__(self, path="data.sqlite3"):
        self.path = path
        self.db = create_engine('sqlite:///' + self.path)

    def test(self):
        self.db.echo = False
        metadata = MetaData(self.db)
        users = Table('users', metadata,
                      Column('user_id', Integer, primary_key=True),
                      Column('name', String(40)),
                      Column('age', Integer),
                      Column('password', String),
                      )
        try:
            users.create()
        except:
            pass

        i = users.insert()
        i.execute(name='Mary', age=30, password='secret')
        i.execute({'name': 'John', 'age': 42},
                  {'name': 'Susan', 'age': 57},
                  {'name': 'Carl', 'age': 33})

        s = users.select()
        rs = s.execute()

        row = rs.fetchone()
        print(row)

if __name__ == "__main__":
    DB = ModuleDatas()
    DB.test()