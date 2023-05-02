import psycopg2 as pg
from config import host, user, password, db_title


class DatabaseManager:
    def __init__(self):
        self.connection = pg.connect(host=host, user=user, password=password, database=db_title)
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()

    def create_table_seen_person(self):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS seen_person(
            id serial,
            id_vk varchar(50) PRIMARY KEY);"""
        )

    def insert_data_seen_person(self, id_vk):
        self.cursor.execute(
            """INSERT INTO seen_person (id_vk) VALUES (%s)""",
            (id_vk,),
        )

    def check(self):
        self.cursor.execute("""SELECT sp.id_vk FROM seen_person AS sp;""")
        return self.cursor.fetchall()

    def delete_table_seen_person(self):
        self.cursor.execute("""DROP TABLE IF EXISTS seen_person CASCADE;""")

    def __del__(self):
        self.cursor.close()
        self.connection.close()


database_manager = DatabaseManager()
database_manager.create_table_seen_person()
print("Database was created!")
