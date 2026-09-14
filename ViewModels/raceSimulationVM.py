from PySide6.QtCore import QObject, Signal

class TrackStatusVM(QObject):
    """
    TODO:
        - refactor track status fetch functions to work with getting info from the db
    """
    #Signals
    updatedTrackSafety = Signal(str) #normal, yellow flag, red flag 
    updatedTrackSurface = Signal(str) #normal, damp, hot, etc.

    def __init__(self):
        super().__init__()
        # on init set Signals and class vars to normal
        self.currentTrackSafety = "normal"
        self.currentTrackSurface = "normal"
        self.updatedTrackSurface.emit(self.currentTrackSurface)
        self.updatedTrackSafety.emit(self.currentTrackSafety)


    def setSurfaceStatus(self, newStatus: str):
        #this could affect 2 views in the Front end so may add a Signal
        if(newStatus != self.currentTrackSurface):
            self.currentTrackSurface = newStatus
            self.updatedTrackSurface.emit(newStatus)

    def setSafetyStatus(self, newStatus: str):
        # might need to run a check that newstatus is an accepted status
        if (newStatus != self.currentTrackSafety):
            self.currentTrackSafety = newStatus
            self.updatedTrackSafety.emit(newStatus)
        else:
            return 0 # no error

    def getSafetyStatus(self):
        return self.currentTrackSafety
    
    def getSurfaceStatus(self):
        return self.currentTrackSurface

    def fetchSafetyStatus(self):
        # fetch status from DB
        #newStatus = dbHandler.getSafetyStatus()
        #stub value need to wright a try except block for getting data from db
        self.setSafetyStatus("test")

    def fetchSurfaceStatus(self):
        # fetch status from DB
        #newStatus = dbHandler.getSafetyStatus()
        #stub value need to wright a try except block for getting data from db
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

    #signal for the current driver(obj)
    updatedFocusDriver = Signal(object)
    #signal for the list of dicts of available drivers "list[drivers]""
    updatedAvailableDrivers = Signal(list)
    # list of dictionaries ([driver: "", team: "", laptime: "", sectionTime: "", placement: "", timeBehind: "" ])
    updatedStandings = Signal(list) #could potentially use this to double for list of active drivers
    def __init__(self):
        super().__init__()
        self.currentFocusDriver

    # Focus Driver Section

    # set the focussed Driver
    #when user selects a user from the driver standings, show specific telemetry for that driver
    def toggleFocusDriver(self, newDriver: object):
        if(newDriver == self.currentFocusDriver):
            self.updateFocusDriver.emit(None)
            self.currentFocusDriver = None
        else:
            self.updatedFocusDriver.emit(newDriver)
            self.currentFocusDriver = newDriver

    #return who the focused driver is
    def getFocusDriver(self):
        return self.focusDriver

    # grab driver telemetry from db
    def fetchDriverTelemetry(self, focusDriver: object):
        focussedData = {"currentLap": 0, "currentGear": 0, "tireLife": 0, "currentSpeed": 0, "currentRPM": 0, "currentFuel": 0.0}
        # current lap, current gear, current tire life, current speed, current RPM, current fuel
        # focussedData = db.getDriverData(focusDriver)
        return focussedData
    
    def refreshData(self):
        """
        grab data from db and update Signals for front end to read

        """
        #fetchDriverTelemetry(focusDriver)
        #fetchDriverStandings()
        #stub
        return 0

    # methods that will attempt to ask db handler for info from db
    def fetchDriverStandings(self):
        #updated list of Dictionaries
        return 0 


class RaceHandler(QObject):
    """
    This will initialize all of the drivers, track info, playControls

    Args:
        QObject (_type_): _description_
    """
    def __init__(self):
            super().__init__()