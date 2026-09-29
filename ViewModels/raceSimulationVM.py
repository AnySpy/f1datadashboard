from PySide6.QtCore import QObject, Signal
from Services.dbhandler import DBhandler


class TrackStatusVM(QObject):
    """
    TODO:
        - refactor track status fetch functions to work with getting info from the db
        - add currentIndex and approxTime to the vars on init
        - add logic to determine if track is wet or dry
    """

    # Signals
    __updatedTrackSafety = Signal(str)  # normal, yellow flag, red flag
    __updatedTrackSurface = Signal(str)  # normal, damp, hot, etc.

    @property
    def updatedTrackSafety(self):
        return self.__updatedTrackSafety

    @property
    def updatedTrackSurface(self):
        return self.__updatedTrackSurface

    def __init__(self, dbHandler: DBhandler):
        super().__init__()
        # on init set Signals and class vars to normal
        self.currentTrackSafety = "normal"
        self.currentTrackSurface = "normal"
        # self.updatedTrackSurface.emit(self.currentTrackSurface)
        # self.updatedTrackSafety.emit(self.currentTrackSafety)
        self.dbHandler = dbHandler
        # fetch status codes from DB on creation

    def setSurfaceStatus(self, newStatus: str):
        # this could affect 2 views in the Front end so may add a Signal
        if newStatus != self.currentTrackSurface:
            self.currentTrackSurface = newStatus
            self.updatedTrackSurface.emit(newStatus)

    def setSafetyStatus(self, newStatus: str):
        """_summary_

        Args:
            newStatus (str): _this is the new status that was grabbed from database_

        Returns:
            _int_: _returns 0 if there are no errors_
        """
        # might need to run a check that newstatus is an accepted status
        if newStatus != self.currentTrackSafety:
            self.currentTrackSafety = newStatus
            self.updatedTrackSafety.emit(newStatus)
        else:
            return 0  # no error

    def getSafetyStatus(self):
        return self.currentTrackSafety

    def getSurfaceStatus(self):
        return self.currentTrackSurface

    #  approxTime: float = 0.00, currentSessionID: int = 1, currentIndex: int = -1, endFlag: bool = False
    def fetchSafetyStatus(self):
        """_grabs data from the dbHandler and calls to set the safety status_"""
        # fetch status from DB
        newStatus = self.dbHandler.getTrackSafetyStatus(
            currentSessionID=1, currentIndex=1, endFlag=False
        )
        # stub value need to wright a try except block for getting data from db
        self.setSafetyStatus(newStatus["message"])

    def fetchSurfaceStatus(self):
        # fetch status from DB
        # newStatus = dbHandler.getSafetyStatus()
        # stub value need to wright a try except block for getting data from db
        self.setSurfaceStatus("test")


class DriverStandingsVM(QObject):
    """_summary_

    Args:
        QObject (_type_): _description_

    Note:
        - This is where we might be able to save a few Signal calls by
          estimating the timing behind the next person.
        - if (there is a <[sometime] seconds difference in placements) send refresh
          else: wait
        - if (new lap): refresh
        - if (new section): refresh

    """

    # signals that need to be sent to the front end code

    # signal for the current driver(obj)
    __updatedFocusDriver = Signal(object)
    # signal for the list of dicts of available drivers "list[drivers]""
    __updatedAvailableDrivers = Signal(list)
    # list of dictionaries ([driver: "", team: "", laptime: "", sectionTime: "", placement: "", timeBehind: "" ])
    __updatedStandings = Signal(
        list
    )  # could potentially use this to double for list of active drivers

    @property 
    def updatedFocusDriver(self):
        return self.__updatedFocusDriver

    @property
    def updatedAvailableDrivers(self):
        return self.__updatedAvailableDrivers

    @property
    def updatedStandings(self):
        return self.__updatedStandings

    def __init__(self):
        super().__init__()
        self.currentFocusDriver

    # Focus Driver Section

    # set the focussed Driver
    # when user selects a user from the driver standings, show specific telemetry for that driver
    def toggleFocusDriver(self, newDriver: object):
        if newDriver == self.currentFocusDriver:
            self.updatedFocusDriver.emit(None)
            self.currentFocusDriver = None
        else:
            self.updatedFocusDriver.emit(newDriver)
            self.currentFocusDriver = newDriver

    # return who the focused driver is
    def getFocusDriver(self):
        return self.currentFocusDriver

    # grab driver telemetry from db
    def fetchDriverTelemetry(self, focusDriver: object):
        focussedData = {
            "currentLap": 0,
            "currentGear": 0,
            "tireLife": 0,
            "currentSpeed": 0,
            "currentRPM": 0,
            "currentFuel": 0.0,
        }
        # current lap, current gear, current tire life, current speed, current RPM, current fuel
        # focussedData = db.getDriverData(focusDriver)
        return focussedData

    def refreshData(self):
        """
        grab data from db and update Signals for front end to read

        """
        # fetchDriverTelemetry(focusDriver)
        # fetchDriverStandings()
        # stub
        return 0

    # methods that will attempt to ask db handler for info from db
    def fetchDriverStandings(self):
        # updated list of Dictionaries
        return 0

class PlayControlsVM(QObject):
    """_summary_

    Args:
        QObject (_type_): _description_
    Methods:
        Skip forward and back
        Play/ Pause
        update Track status marks on playcontrols

    Notes:
        - The seconds will need to interact with the player standings so that 
          we don't have to constantly send updates from the View Model
        - This will also need to interact with race simulation
        WHAT THIS NEEDS TO WORK 
        - needs to have the total session time for each selected session
        - needs to be able to show current time and total time on front end
        - needs to be able to change current time
        - needs to be able to play / pause simulation
    """
    updatedTime = Signal(float)
    raceDuration = Signal(float)
    # used to display time on play back slider
    updatedFormattedTime = Signal(str)
    def __init__(self):
        super().__init__()
        self.isPlaying: bool = False
        self.currentTime:float = 0.00

    def togglePlay(self):
        #stub
        return 0 
    def setCurrentTime(self):
        # make what ever is reading the data convert the convert the time to a string and update the updatedTime hour: minute: second
        return 0
    def setRaceDuration(self):
        """
        query lap 1 
        """
        print("setting race duration")

    def seek(self):
        #stub
        return 0
    
    


class RaceHandler(QObject):
    """
    This will initialize all of the drivers, track info, playControls

    Args:
        QObject (_type_): _description_
    """

    def __init__(self):
        super().__init__()
