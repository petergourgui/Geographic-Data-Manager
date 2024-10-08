from p2app.engine import app_logic
from p2app.engine import region_logic
from p2app.engine import country_logic
from p2app.engine import continent_logic



class Engine:
    """An object that represents the application's engine, whose main role is to
    process events sent to it by the user interface, then generate events that are
    sent back to the user interface in response, allowing the user interface to be
    unaware of any details of how the engine is implemented.
    """

    def __init__(self):
        """Initializes the engine"""
        self._connection = None
        self.app_handler = app_logic.AppHandler()
        self.continent_handler = None
        self.country_handler = None
        self.region_handler = None


    def process_event(self, event):
        """A generator function that processes one event sent from the user interface,
        yielding zero or more events in response."""
        response = None
        if self.app_handler.is_app_related(event):
            response = self.app_handler.handle_event(event)
            if type(response) == tuple:
                self._connection = response[1]
                self.continent_handler = continent_logic.ContinentHandler(self._connection)
                self.country_handler = country_logic.CountryHandler(self._connection)
                self.region_handler = region_logic.RegionHandler(self._connection)
                response = response[0]
            yield response
        elif self.continent_handler.is_continent_related(event):
            response = self.continent_handler.handle_event(event)
            if type(response) == list:
                for continent_event in response:
                    yield continent_event
            else:
                yield response
        elif self.country_handler.is_country_related(event):
            response = self.country_handler.handle_event(event)
            if type(response) == list:
                for country_event in response:
                    yield country_event
            else:
                yield response
        elif self.region_handler.is_region_related(event):
            response = self.region_handler.handle_event(event)
            if type(response) == list:
                for region_event in response:
                    yield region_event
            else:
                yield response


