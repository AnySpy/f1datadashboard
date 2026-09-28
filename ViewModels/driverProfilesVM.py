from PySide6.QtCore import QObject, Signal, QByteArray, Qt
from Services.stat_scraper import DriverStatScraper
from Services.dbhandler import DBhandler
from PySide6.QtGui import QPixmap, QPainter, QPainterPath


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

    stats_loaded = Signal(dict)
    bio_loaded = Signal(str)
    name_loaded = Signal(str)
    img_loaded = Signal(QPixmap)

    def __init__(self, dbhandler: DBhandler):
        """Generic initialization of the `DriverProfilesViewModel` class

        Args:
            dbhandler (DBhandler): A `DBhandler` object that will be used to communicate with the database. Should be passed from `main.py`
        """
        super().__init__()

        self.dbhandler = dbhandler

        self.scraper = DriverStatScraper()
        # ? Initializing this here in case we need to remember this data between state changes. It'd be easy to remove this later if we want to.
        self.current_stats: dict[str, str] = {}

    def _get_known_drivers(self) -> dict[str, str]:
        """Helper function for `get_driver_names()` and `get_driver_codes()`

        Returns:
            dict[str, str]: A dictionary with the driver codes as keys and the driver names as values (e.g. {'VER': 'Max Verstappen'})
        """
        return self.dbhandler.getKnownDrivers()

    def get_driver_names(self) -> list[str]:
        """Gets a list of all known driver names

        Returns:
            list[str]: A list containing all names as strings.
        """
        dict = self._get_known_drivers()

        return list(dict.values())

    def get_driver_codes(self) -> list[str]:
        """Gets a list of all known driver codes

        Returns:
            list[str]: A list containing all codes as strings
        """
        dict = self._get_known_drivers()

        return list(dict.keys())

    def get_driver_bio(self, driver_name: str) -> str:
        """Gets the driver bio as a string

        Args:
            driver_name (str): The name of the driver in firstname-lastname format (e.g. "max-verstappen")

        Returns:
            str: The biography of the driver
        """
        return self.scraper.fetch_driver_bio(driver_name)

    def get_driver_image(self, driver_name: str) -> QPixmap:
        """Returns the driver image formatted to be the profile image for the driver profile.

        Args:
            driver_name (str): Name of the driver provided in the format "firstname-lastname" (e.g. "max-verstappen")

        Returns:
            QPixmap: A canvas object that is ready to be displayed to the user.
        """
        img_bytes = self.scraper.fetch_driver_image(driver_name)
        pixmap = QPixmap()

        if img_bytes and pixmap.loadFromData(QByteArray(img_bytes)):
            pass
        else:
            # TODO: This should be replaced with a generic "Driver Not Found" eventually
            pixmap = QPixmap("images/sample_driver.jpg")

        # ? The idea is that we scale the image down to 100x100, create a canvas object of the same size,
        # ?     create a painter object with a circular path that then paints the image as a circle onto the canvas,
        # ?     and then creates a label holder for that image to display the canvas in the UI.
        # ? It's kind of disgusting and I hate it but I couldn't figure out how to do it in QSS. If we could figure that out, it'd be much better.
        image = pixmap.scaled(
            100,
            100,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        canvas = QPixmap(100, 100)
        canvas.fill(Qt.GlobalColor.transparent)
        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter_path = QPainterPath()
        painter_path.addEllipse(0, 0, 100, 100)
        painter.setClipPath(painter_path)
        painter.drawPixmap(0, 0, image)
        painter.end()

        return canvas

    def get_formatted_placements(
        self, placement_history: list[int], location_history: list[str]
    ) -> list[tuple[str, str]]:
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
        """Helper function: called by `get_formatted_placements()`"""
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

    def _load_driver_stats(self, driver_name: str, scope: str) -> dict[str, str]:
        """Loads the driver stats from the F1 website

        Args:
            driver_name (str): The name of the driver in firstname-lastname format (e.g. "max-verstappen")
            scope (str): Whether to use the scope of "season" or "career" for stats.

        Returns:
            dict[str, str]: The stats returned in a pairing of "Title": "Value"
        """
        data = self.scraper.fetch_driver_stats(driver_name)

        if not data:
            return {"ERROR": "Data Unavailable"}

        self.current_stats = data[scope]

        return self.current_stats

    def get_season_stats(self, driver_name: str) -> dict[str, str]:
        """Returns the given driver's season stats

        Args:
            driver_name (str): Name of the driver provided in the format "firstname-lastname" (e.g. "max-verstappen")

        Returns:
            dict[str, str]: A dictionary containing the key of the title of the stat and the value of the value of said stat.
        """
        return self._load_driver_stats(driver_name, "season")

    def get_career_stats(self, driver_name: str):
        """Returns the given driver's career stats

        Args:
            driver_name (str): Name of the driver provided in the format "firstname-lastname" (e.g. "max-verstappen")

        Returns:
            dict[str, str]: A dictionary containing the key of the title of the stat and the value of the value of said stat.
        """
        return self._load_driver_stats(driver_name, "career")

    def select_driver(self, driver_code: str):
        """Binds to the signal objects from the driverProfiles to update the display

        Args:
            driver_code (str): The code of the driver (e.g. Max Verstappen would be `VER`)
        """
        driver_dict = self._get_known_drivers()

        driver_name = driver_dict[driver_code]
        # ? We store a copy of the driver name to display before replacing it for URL purposes
        _driver_display_name = driver_name
        driver_name = driver_name.lower().replace(" ", "-")

        career_stats = self.get_career_stats(driver_name)
        bio_text = self.get_driver_bio(driver_name)
        driver_img = self.get_driver_image(driver_name)

        if not career_stats:
            career_stats = {"Status": "No Stats Available"}
        if not bio_text:
            bio_text = "Biography Not Available."

        self.stats_loaded.emit(career_stats)
        self.bio_loaded.emit(bio_text)
        self.name_loaded.emit(_driver_display_name)
        self.img_loaded.emit(driver_img)

    def setActiveDriver(self):
        # stub
        return 0

    # dataType historical, seasonData, teamData
    def fetchDriverData(self, session: str):
        # stub
        return 0


def _main():
    dbhandler = DBhandler()

    vm_test = DriverProfilesViewModel(dbhandler)
    data = vm_test.get_driver_codes()
    print(data)
    data = vm_test.get_driver_names()
    print(data)

    return 0


if __name__ == "__main__":
    _main()
