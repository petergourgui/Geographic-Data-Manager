from p2app.events import continents
from p2app.events import app

class ContinentHandler:
    def __init__(self, connection):
        self._connection = connection
        self._current_id = 8


    def handle_event(self, event):
        """Handles events that are continent related and returns a responding event"""
        if isinstance(event, continents.StartContinentSearchEvent):
            continent_code = event.continent_code()
            continent_name = event.name()
            found_continents = self._find_continents(continent_code, continent_name)
            return found_continents

        if isinstance(event, continents.LoadContinentEvent):
            continent_id = event.continent_id()
            return self._get_continent(continent_id)

        if isinstance(event, continents.SaveNewContinentEvent):
            continent = event.continent()
            continent_code = continent.continent_code
            continent_name = continent.name
            return self._insert_continent(continent_code, continent_name)

        if isinstance(event, continents.SaveContinentEvent):
            continent = event.continent()
            continent_id = continent.continent_id
            continent_code = continent.continent_code
            continent_name = continent.name
            return self._update_continent(continent_id, continent_code, continent_name)


    @staticmethod
    def is_continent_related(event) -> bool:
        """Checks if the given event is continent related"""
        if isinstance(event, continents.StartContinentSearchEvent):
            return True
        if isinstance(event, continents.LoadContinentEvent):
            return True
        if isinstance(event, continents.SaveNewContinentEvent):
            return True
        if isinstance(event, continents.SaveContinentEvent):
            return True

        return False


    def _get_continent(self, continent_id: int):
        """Returns a ContinentLoadedEvent containing information about the given continent"""
        try:
            cursor = self._connection.execute("""
            SELECT continent_code, name
            FROM continent
            WHERE continent_id = ?;""", (continent_id, ))
            continent = cursor.fetchone()
            cursor.close()
            return continents.ContinentLoadedEvent(continents.Continent(continent_id, continent[0], continent[1]))
        except:
            return app.ErrorEvent('Unable to load the continent!')


    def _find_continents(self, continent_code: str, continent_name: str) -> list:
        """Finds all continents in the database that match the given continent code and name
        and returns a list of those continents"""
        found_continents = []
        if not continent_code:
            cursor = self._connection.execute('''
            SELECT continent_id, continent_code
            FROM continent
            WHERE name = ?;''', (continent_name,))
            while True:
                continent = cursor.fetchone()
                if not continent:
                    cursor.close()
                    break
                found_continents.append(continents.ContinentSearchResultEvent(continents.Continent(continent[0], continent[1], continent_name)))

        elif not continent_name:
            cursor = self._connection.execute('''
            SELECT continent_id, name
            FROM continent
            WHERE continent_code = ?;''', (continent_code,))
            while True:
                continent = cursor.fetchone()
                if not continent:
                    cursor.close()
                    break
                found_continents.append(continents.ContinentSearchResultEvent(continents.Continent(continent[0], continent_code, continent[1])))

        else:
            cursor = self._connection.execute('''
            SELECT continent_id
            FROM continent
            WHERE name = ? AND continent_code = ?;''', (continent_name, continent_code))
            while True:
                continent = cursor.fetchone()
                if not continent:
                    cursor.close()
                    break
                found_continents.append(continents.ContinentSearchResultEvent(continents.Continent(continent[0], continent_code, continent_name)))

        return found_continents


    def _insert_continent(self, continent_code: str, continent_name: str):
        """Inserts a new continent into the database with the specified ID, code, and name.
        Returns a success or fail event depending on whether the insertion was successful."""
        continent_id = self._current_id
        try:
            self._connection.execute("""
            INSERT INTO continent (continent_id, continent_code, name)
            VALUES (?, ?, ?)""", (continent_id, continent_code, continent_name))
            self._current_id += 1
            return continents.ContinentSavedEvent(continents.Continent(continent_id, continent_code, continent_name))
        except:
            return continents.SaveContinentFailedEvent('The entered values are invalid! Continent code must be unique!')


    def _update_continent(self, continent_id: int, continent_code: str, continent_name: str):
        """Modifies a continent into the database with the specified ID, code, and name.
        Returns a success or fail event depending on whether the modification was successful."""
        try:
            self._connection.execute("""
            UPDATE continent
            SET continent_code = ?, name = ?
            WHERE continent_id = ?;""", (continent_code, continent_name, continent_id))
            return continents.ContinentSavedEvent(continents.Continent(continent_id, continent_code, continent_name))
        except:
            return continents.SaveContinentFailedEvent('The entered values are invalid! Continent code must be unique!')