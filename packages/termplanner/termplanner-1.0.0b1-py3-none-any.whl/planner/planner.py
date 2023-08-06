# Created by Alex Hurtado
import sqlite3
import click
import os


class Planner(object):
    """Defines a Planner class"""
    def __init__(self, db_name='planner.db'):
        self.db_name = db_name
        self.connected = None

        self.PATH = os.path.dirname(os.path.realpath(__file__))
        self.db = self.PATH + "\\"+ self.db_name

    def make_db(self):
        """Makes a database, if it doesn't exist already"""

        self.open_connection()
        self.cur.execute('''CREATE TABLE events
                              (date text, events_name text)''')
        self.conn.commit()

    def open_connection(self):
        """Opens a database connection."""
        if not self.connected:
            self.conn = sqlite3.connect(self.db)
            self.connected = True
            self.cur = self.conn.cursor()

    def close_connection(self):
        """Closes the database connection."""
        if self.check_connection():
            self.cur.close()
            self.conn.close()
            self.connected = False

    def check_connection(self):
        """Checks to see if a connection is open"""
        if self.connected:
            return True

        else:
            return False

    def create_event(self, date, event):
        """Creates an event inside of a database"""
        if not self.connected:
            self.open_connection()

        self.cur.execute('INSERT INTO events (date, events_name) VALUES (?, ?)', (date, event))
        self.conn.commit()
        
    def read_all(self):
        """Reads the whole database and prints it out"""
        click.echo("Collecting data from database....")
        self.info = self.cur.execute('''SELECT * FROM events''').fetchall()
        click.echo("Here are the events that you have set: ")
        for i in self.info:
            click.echo(i)

    def checkout(self, event, allow_list):
        """User controlled option to remove event from database."""
        if not self.connected:
            self.open_connection()

        self.cur.execute('DELETE FROM events WHERE events_name=(?)', (event,))
        self.conn.commit()

        if allow_list:
            self.read_all()
