from PySide6.QtCore import QObject, Signal

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

    def setActiveDriver(self):
        #stub
        return 0

    #dataType historical, seasonData, teamData
    def fetchDriverData(self, session: str):
        #stub
        return 0

    
