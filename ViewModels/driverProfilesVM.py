from PySide6.QtCore import QObject, Signal
from Services.stat_scraper import DriverStatScraper
import typing

class DriverProfilesViewModel(QObject):
    """_summary_

    Args:
        QObject (_type_): _description_

    Methods:
        - fetchDriverInfo(season, session, race)

    
    Variables:
        - driver1 from class
        - driver2 from class

    """

    def __init__(self):
        super().__init__()

        self.scraper = DriverStatScraper()
        # ? Initializing this here in case we need to remember this data between state changes. It'd be easy to remove this later if we want to.
        self.current_stats: dict[str, str] = {}

    def get_formatted_placements(self, placement_history: list[int], location_history: list[str]) -> list[tuple[str, str]]:
        """When supplied with a list of placement history and the corresponding locations of those placements, will format the placement and place them in a tuple

        Args:
            placement_history (list[int]): The list of placements of the drivers as integers
            location_history (list[str]): The list of 

        Returns:
            list[tuple[str, str]]: _description_
        """
        formatted_cards = []
        for place, location in zip(placement_history, location_history):
            formatted_place = self._format_placement(place)
            formatted_cards.append((formatted_place, location))

        return formatted_cards

    def _format_placement(self, place: int) -> str:
        """Helper function: called by get_formatted_placements"""
        match place:
            case 1:
                placement_string = "1st"
            case 2:
                placement_string = "2nd"
            case 3:
                placement_string = "3rd"
            case _:
                placement_string = f"{place}th"
        return placement_string

    def load_driver_stats(self, driver_name: str) -> dict[str, str]:
        """Loads the driver stats from the F1 website

        Args:
            driver_name (str): The name of the driver in firstname-lastname format (e.g. "max-verstappen")

        Returns:
            dict[str, str]: The stats 
        """
        data = self.scraper.fetch_driver_stats(driver_name)

        if not data:
            self.current_stats = {"ERROR": "Data Unavailable"}
        else:
            self.current_stats = data

        return self.current_stats
            

    def setActiveDriver(self):
        #stub
        return 0

    #dataType historical, seasonData, teamData
    def fetchDriverData(self, session: str):
        #stub
        return 0

    
