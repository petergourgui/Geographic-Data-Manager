from p2app.events import countries
from p2app.events import app


class CountryHandler:
    def __init__(self, connection):
        self._connection = connection
        self._current_id = 350210


    def handle_event(self, event):
        """Handles events that are country related and returns a responding event"""
        if isinstance(event, countries.StartCountrySearchEvent):
            country_code = event.country_code()
            country_name = event.name()
            found_countries = self._find_countries(country_code, country_name)
            return found_countries
        if isinstance(event, countries.LoadCountryEvent):
            country_id = event.country_id()
            return self._get_country(country_id)
        if isinstance(event, countries.SaveNewCountryEvent):
            country = event.country()
            country_id = country.country_id
            country_code = country.country_code
            country_name = country.name
            continent_id = country.continent_id
            wiki_link = country.wikipedia_link
            keywords = country.keywords
            return self._insert_country(country_code, country_name, continent_id, wiki_link, keywords)
        if isinstance(event, countries.SaveCountryEvent):
            country = event.country()
            country_id = country.country_id
            country_code = country.country_code
            country_name = country.name
            continent_id = country.continent_id
            wiki_link = country.wikipedia_link
            keywords = country.keywords
            return self._update_country(country_id, country_code, country_name, continent_id, wiki_link, keywords)

    @staticmethod
    def is_country_related(event) -> bool:
        """Checks if the given event is country related"""
        if isinstance(event, countries.StartCountrySearchEvent):
            return True
        if isinstance(event, countries.LoadCountryEvent):
            return True
        if isinstance(event, countries.SaveNewCountryEvent):
            return True
        if isinstance(event, countries.SaveCountryEvent):
            return True

        return False


    def _find_countries(self, country_code: str, country_name: str) -> list:
        """Finds all countries in the database that match the given country code and name
        and returns a list of those countries"""
        found_countries = []
        if not country_code:
            cursor = self._connection.execute('''
            SELECT *
            FROM country
            WHERE name = ?;''', (country_name,))
            while True:
                country = cursor.fetchone()
                if not country:
                    cursor.close()
                    break
                found_countries.append(countries.CountrySearchResultEvent(countries.Country(*country)))

        elif not country_name:
            cursor = self._connection.execute('''
            SELECT *
            FROM country
            WHERE country_code = ?;''', (country_code,))
            while True:
                country = cursor.fetchone()
                if not country:
                    cursor.close()
                    break
                found_countries.append(countries.CountrySearchResultEvent(countries.Country(*country)))

        else:
            cursor = self._connection.execute('''
            SELECT *
            FROM country
            WHERE name = ? AND country_code = ?;''', (country_name, country_code))
            while True:
                country = cursor.fetchone()
                if not country:
                    cursor.close()
                    break
                found_countries.append(countries.CountrySearchResultEvent(countries.Country(*country)))

        return found_countries


    def _get_country(self, country_id: int):
        """Returns a CountryLoadedEvent containing information about the given country"""
        try:
            cursor = self._connection.execute("""
            SELECT *
            FROM country
            WHERE country_id = ?;""", (country_id, ))
            country = cursor.fetchone()
            cursor.close()
            return countries.CountryLoadedEvent(countries.Country(*country))
        except:
            return app.ErrorEvent('Unable to load the country!')


    def _insert_country(self, country_code, name, continent_id, wiki_link, keywords):
        """Inserts a new country into the database with the items.
        Returns a success or fail event depending on whether the insertion was successful."""
        country_id = self._current_id
        if not keywords:
            keywords = None
        if not wiki_link:
            wiki_link = ''

        country_details = (country_id, country_code, name, continent_id, wiki_link, keywords)
        try:
            self._connection.execute("""
            INSERT INTO country (country_id, country_code, name, continent_id, wikipedia_link, keywords)
            VALUES (?, ?, ?, ?, ?, ?)""", (country_id, country_code, name, continent_id, wiki_link, keywords))
            self._current_id += 1
            return countries.CountrySavedEvent(countries.Country(*country_details))
        except:
            return countries.SaveCountryFailedEvent('The entered values are invalid! Make sure continent ID exists and country code is unique!')


    def _update_country(self, country_id, country_code, name, continent_id, wiki_link, keywords):
        """Modifies a country into the database with the specified items.
        Returns a success or fail event depending on whether the modification was successful."""
        if not keywords:
            keywords = None
        if not wiki_link:
            wiki_link = ''

        country_details = (country_id, country_code, name, continent_id, wiki_link, keywords)
        try:
            self._connection.execute("""
            UPDATE country
            SET country_code = ?, name = ?, continent_id = ?, wikipedia_link = ?, keywords = ?
            WHERE country_id = ?;""", (country_code, name, continent_id, wiki_link, keywords, country_id))
            return countries.CountrySavedEvent(countries.Country(*country_details))
        except:
            return countries.SaveCountryFailedEvent('The entered values are invalid! Make sure continent ID exists and country code is unique!')