from p2app.events import app
from p2app.events import database
import sqlite3

class AppHandler:
    def __init__(self):
        self._connection = None


    def handle_event(self, event):
        """Handles events at the application level and returns a responding event"""
        if isinstance(event, app.QuitInitiatedEvent):
            return self._quit_app()
        if isinstance(event, database.OpenDatabaseEvent):
            return self._open_database(event)
        if isinstance(event, database.CloseDatabaseEvent):
            return self._close_database()


    @staticmethod
    def is_app_related(event) -> bool:
        """Checks if the given event can be handled on the application level"""
        if isinstance(event, app.QuitInitiatedEvent):
            return True
        if isinstance(event, database.OpenDatabaseEvent):
            return True
        if isinstance(event, database.CloseDatabaseEvent):
            return True

        return False


    def _quit_app(self):
        """Quits the app and ends the program. Closes the connection if it exists."""
        if self._connection is not None:
            self._connection.close()
        return app.EndApplicationEvent()


    def _open_database(self, event):
        """Opens a database and returns an event of success or failure.
        If the database is successfully opened, a SQLite connection is returned."""
        database_path = event.path()
        if database_path.suffix != '.db':
            return database.DatabaseOpenFailedEvent('The chosen file is not a database!')

        self._connection = sqlite3.connect(database_path)
        try:
            cursor = self._connection.execute(
                '''SELECT *
                   FROM airport
                   WHERE airport_ident = 'KSNA';''')
            cursor.close()
            self._connection.execute('PRAGMA foreign_keys = ON;')
            return database.DatabaseOpenedEvent(database_path), self._connection
        except:
            self._connection.close()
            return database.DatabaseOpenFailedEvent('The chosen database is not compatible with the application!')


    def _close_database(self):
        """Closes the opened database and returns an event of success or failure.
        If the database is successfully closed, the corresponding SQLite connection is closed."""
        self._connection.close()
        return database.DatabaseClosedEvent()

