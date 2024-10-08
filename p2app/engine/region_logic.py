from p2app.events import regions
from p2app.events import app


class RegionHandler:
    def __init__(self, connection):
        self._connection = connection
        self._current_id = 354602


    def handle_event(self, event):
        """Handles events that are region related and returns a responding event"""
        if isinstance(event, regions.StartRegionSearchEvent):
            region_code = event.region_code()
            region_name = event.name()
            local_code = event.local_code()
            found_regions = self._find_regions(region_code, local_code, region_name)
            return found_regions
        if isinstance(event, regions.LoadRegionEvent):
            region_id = event.region_id()
            return self._get_region(region_id)
        if isinstance(event, regions.SaveNewRegionEvent):
            region = event.region()
            return self._insert_region(region.region_code, region.local_code, region.name,
                                       region.continent_id, region.country_id, region.wikipedia_link, region.keywords)
        if isinstance(event, regions.SaveRegionEvent):
            region = event.region()
            return self._update_region(region.region_id, region.region_code, region.local_code, region.name,
                                       region.continent_id, region.country_id, region.wikipedia_link, region.keywords)


    @staticmethod
    def is_region_related(event) -> bool:
        """Checks if the given event is region related"""
        if isinstance(event, regions.StartRegionSearchEvent):
            return True
        if isinstance(event, regions.LoadRegionEvent):
            return True
        if isinstance(event, regions.SaveNewRegionEvent):
            return True
        if isinstance(event, regions.SaveRegionEvent):
            return True

        return False


    def _find_regions(self, region_code: str, local_code: str, region_name: str) -> list:
        """Finds all regions in the database that match the given items
        and returns a list of those regions"""
        found_regions = []

        if not region_code and not local_code:
            cursor = self._connection.execute('''
            SELECT *
            FROM region
            WHERE name = ?;''', (region_name, ))
            while True:
                region = cursor.fetchone()
                if not region:
                    cursor.close()
                    break
                found_regions.append(regions.RegionSearchResultEvent(regions.Region(*region)))
        elif not region_code and not region_name:
            cursor = self._connection.execute('''
            SELECT *
            FROM region
            WHERE local_code = ?;''', (local_code, ))
            while True:
                region = cursor.fetchone()
                if not region:
                    cursor.close()
                    break
                found_regions.append(regions.RegionSearchResultEvent(regions.Region(*region)))
        elif not local_code and not region_name:
            cursor = self._connection.execute('''
            SELECT *
            FROM region
            WHERE region_code = ?;''', (region_code, ))
            while True:
                region = cursor.fetchone()
                if not region:
                    cursor.close()
                    break
                found_regions.append(regions.RegionSearchResultEvent(regions.Region(*region)))
        elif not region_code:
            cursor = self._connection.execute('''
            SELECT *
            FROM region
            WHERE local_code = ? AND name = ?;''', (local_code, region_name))
            while True:
                region = cursor.fetchone()
                if not region:
                    cursor.close()
                    break
                found_regions.append(regions.RegionSearchResultEvent(regions.Region(*region)))
        elif not local_code:
            cursor = self._connection.execute('''
            SELECT *
            FROM region
            WHERE region_code = ? AND name = ?;''', (region_code, region_name))
            while True:
                region = cursor.fetchone()
                if not region:
                    cursor.close()
                    break
                found_regions.append(regions.RegionSearchResultEvent(regions.Region(*region)))
        elif not region_name:
            cursor = self._connection.execute('''
            SELECT *
            FROM region
            WHERE region_code = ? AND local_code = ?;''', (region_code, local_code))
            while True:
                region = cursor.fetchone()
                if not region:
                    cursor.close()
                    break
                found_regions.append(regions.RegionSearchResultEvent(regions.Region(*region)))
        else:
            cursor = self._connection.execute('''
            SELECT *
            FROM region
            WHERE region_code = ? AND local_code = ? AND name = ?;''', (region_code, local_code, region_name))
            while True:
                region = cursor.fetchone()
                if not region:
                    cursor.close()
                    break
                found_regions.append(regions.RegionSearchResultEvent(regions.Region(*region)))

        return found_regions


    def _get_region(self, region_id: int):
        """Returns a RegionLoadedEvent containing information about the given region"""
        try:
            cursor = self._connection.execute("""
            SELECT *
            FROM region
            WHERE region_id = ?;""", (region_id, ))
            region = cursor.fetchone()
            cursor.close()
            return regions.RegionLoadedEvent(regions.Region(*region))
        except:
            return app.ErrorEvent('Unable to load the region!')


    def _insert_region(self, region_code, local_code, name, continent_id, country_id, wiki_link, keywords):
        """Inserts a new region into the database with the items.
        Returns a success or fail event depending on whether the insertion was successful."""
        region_id = self._current_id
        if not keywords:
            keywords = None
        if not wiki_link:
            wiki_link = None

        region_details = (region_id, region_code, local_code, name, continent_id, country_id, wiki_link, keywords)
        try:
            self._connection.execute("""
            INSERT INTO region (region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (region_id, region_code, local_code, name, continent_id, country_id, wiki_link, keywords))
            self._current_id += 1
            return regions.RegionSavedEvent(regions.Region(*region_details))
        except:
            return regions.SaveRegionFailedEvent('The entered values are invalid! Make sure continent and '
                                                 'country ID exist, and region code is unique!')


    def _update_region(self, region_id, region_code, local_code, name, continent_id, country_id, wiki_link, keywords):
        """Modifies a country into the database with the specified items.
        Returns a success or fail event depending on whether the modification was successful."""
        if not keywords:
            keywords = None
        if not wiki_link:
            wiki_link = None

        region_details = (region_id, region_code, local_code, name, continent_id, country_id, wiki_link, keywords)
        try:
            self._connection.execute("""
            UPDATE region
            SET region_code = ?, local_code = ?, name = ?, continent_id = ?, country_id = ?, wikipedia_link = ?, keywords = ?
            WHERE region_id = ?;""", (region_code, local_code, name, continent_id, country_id, wiki_link, keywords, region_id))
            return regions.RegionSavedEvent(regions.Region(*region_details))
        except:
            return regions.SaveRegionFailedEvent('The entered values are invalid! Make sure continent and '
                                                 'country ID exist, and region code is unique!')