#!/usr/bin/python3
import sqlite3

class NoteMeta:
    def __init__(self, id, date, time):
        self.id = id
        self.date = date
        self.time = time


class Note:
    def __init__(self, message="", note_meta=None):
        self.message = message
        self.note_meta = note_meta


class Repository:
    def __init__(self, database_path, table_name):
        self.database = sqlite3.connect(database_path)
        self.table_name = table_name
        create = """CREATE TABLE IF NOT EXISTS '{table_name}' (
                         'ID' INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                         'Date' TEXT NOT NULL,
                         'Time' TEXT NOT NULL,
                         'Note' TEXT NOT NULL
                      );"""
        cursor = self.database.cursor()
        cursor.execute(create.format(table_name=self.table_name))
        self.database.commit()
        cursor.close()

    def get_last(self):
        cursor = self.database.cursor()
        select_request = f"""SELECT * FROM "{self.table_name}"
                            ORDER BY ID DESC LIMIT 1;"""
        cursor.execute(select_request)
        row = cursor.fetchall()[0]
        return Note(row[3], NoteMeta(row[0], row[1], row[2])) if row else None

    def select_notes(self, note_id=None, date=None, time=None, message=None):
        cursor = self.database.cursor()
        select_request = f"""SELECT * FROM "{self.table_name}" """
        if note_id is not None or date is not None or time is not None or message is not None:
            select_request += "WHERE "
        if note_id is not None:
            select_request += f"ID = {note_id}"
        if date is not None:
            select_request += f"Date = '{date}'"
        if time is not None:
            select_request += f"Time = '{time}'"
        if message is not None:
            select_request += f"Note = '{message}'"

        cursor.execute(select_request)
        rows = cursor.fetchall()
        return [Note(l_message, NoteMeta(l_id, l_date, l_time)) for l_id, l_date, l_time, l_message in rows]

    def append_note(self, note):
        if not note:
            return
        cursor = self.database.cursor()
        insert = f"""INSERT INTO {self.table_name} (Date, Time, Note)
                        VALUES (date('now', 'localtime'), time('now', 'localtime'), '{note.message}')"""
        cursor.execute(insert)
        self.database.commit()
        cursor.close()

    def update_note(self, note):
        if not note:
            return
        cursor = self.database.cursor()
        update =    f"""UPDATE {self.table_name} 
                        SET Note = '{note.message}'
                        WHERE 
                        ID = {note.note_meta.id}"""
        cursor.execute(update)
        self.database.commit()
        cursor.close()

    def delete_note(self, note):
        if not note:
            return
        cursor = self.database.cursor()
        delete =    f"""DELETE FROM {self.table_name} 
                        WHERE ID = {note.note_meta.id}"""
        cursor.execute(delete)
        self.database.commit()
        cursor.close()