from PySide6.QtCore import QObject, Signal, QTimer
from Services.dbhandler import DBhandler

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
        QObject: _this just allows use of Signals_
    Methods:
        Skip forward and back
        Play/ Pause
        update Track status marks on playcontrols

    Notes:
        - The seconds will need to interact with the player standings so that 
          we don't have to constantly send updates from the View Model
        - This will also need to interact with race simulation
        - make sure that this doesn't need to ping the signal every millisecond 
          only update the signals on important changes (togglePlay, newSection, newLap).
          might need to implement some time correcting if the other vms get out of sync
        WHAT THIS NEEDS TO WORK 
        - needs to have the total session time for each selected session
        - needs to be able to show current time and total time on front end
        - needs to be able to change current time
        - needs to be able to play / pause simulation
    """
    updatedTime = Signal(float)
    updatedRaceDuration = Signal(float)
    # this should probably be a property of play controls it will need to listen to changes
    updatedPlayingStatus = Signal(bool)
    # used to display time on play back slider
    # updatedFormattedTime = Signal(str)
    def __init__(self):
        super().__init__()
        self.isPlaying: bool = False
        self.currentTime:float = 0.00
        self.currentRaceDuration: float = 0.00
        # read only 
        self.dbhandler = DBhandler()
        # load session times to the session table
        # self.fetchRaceDuration(self.currentSessionID)
        # slider properties
        
        # create timer
        self.timer = QTimer(self)
        # set interval to 1000ms or 1 second smallest measurement we need
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._tick)
        # test
        self.timer.start()


    def _tick(self):
        # print(f"timer = {self.currentTime + 1}")
        self.setCurrentTime(self.currentTime + 1)

    def togglePlay(self, timeAtTogglePressed):
        # if simulation is playing then pause
        if(self.isPlaying):
            self.isPlaying = False
            self.updatedPlayingStatus.emit(False)
            self.timer.stop()
            self.setCurrentTime(timeAtTogglePressed)
        else:
            self.isPlaying = True
            self.updatedPlayingStatus.emit(True)
            self.timer.start()

    def setCurrentTime(self, newCurrentTime):
        # make what ever is reading the data convert the convert the time to a string and update the updatedTime hour: minute: second
        self.currentTime = newCurrentTime
        self.updatedTime.emit(newCurrentTime)
        
    def fetchRaceDuration(self, sessionID) -> float:
        """
        query lap 1 
        """
        totalDuration: float = self.dbhandler.getSessionTime(sessionID)
        # might need to handle if the value is None
        self.setRaceDuration(totalDuration)

    def setRaceDuration(self, newDuration: float):
        print(f"raceSimulationVM.py/PlayControlsVM/setRaceDuration: attempting to set new duration to {newDuration}")
        if(newDuration != self.currentRaceDuration):
            self.currentRaceDuration = newDuration
            print(f"raceSimulationVM.py/setRaceDuration: newDuration is different from currentDuration so send a signal to update")
            self.updatedRaceDuration.emit(newDuration)
            

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
