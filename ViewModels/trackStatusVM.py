from PySide6.QtCore import QObject, Signal
from Services.dbhandler import DBhandler
from ViewModels.raceSimulationVM import PlayControlsVM
class TrackStatusVM(QObject):
    """
    TODO:
        - refactor track status fetch functions to work with getting info from the db
        - add currentIndex and approxTime to the vars on init
        - add logic to determine if track is wet or dry
    """

    # Signals
    __updatedTrackSafety = Signal(str)  
    __updatedTrackSurface = Signal(str)  

    @property
    def updatedTrackSafety(self):
        return self.__updatedTrackSafety

    @property
    def updatedTrackSurface(self):
        return self.__updatedTrackSurface

    def __init__(self, playControlsVM: PlayControlsVM):
        super().__init__()
        # on init set Signals and class vars to normal
        self.currentTrackSafety: str = "session data not loaded..."
        self.currentTrackSurface = "normal"
        self.currentIndex: int = 1
        self.currentSessionId: int = 1
        # NOTE: flagged for depreciation once playcontrolsVM updates all viewModels
        self.currentTime: float = 0.00
        self.lastStatusChangeTime: float | None = 0.0
        self.nextStatusChangeTime: float | None = 0.0
        self.playControlsVM = playControlsVM
        # on playcontrol _tick for clock run _onCurrentTimeChange function
        self.playControlsVM.updatedTime.connect(self._onCurrentTimeChange)

        # create a new DBhandler for fetching track info
        """
            NOTE: Read only
        """
        self.dbHandler = DBhandler()
        # fetch status codes from DB on creation

    def _onCurrentTimeChange(self, newCurrentTime):
        # if newCurrentTime < self.lastStatusChangeTime then the scrubber has been used to go back in time
        if((newCurrentTime < self.lastStatusChangeTime) or (newCurrentTime >= self.nextStatusChangeTime)):
            # fetch safety status based off of time
            print(f"trackStatusVM.py/TrackStatusVM/_onCurrentTimeChange: Fetch status via time newCurrentTime: {newCurrentTime}, lastStatusChangeTime: {self.lastStatusChangeTime}")
            self.fetchSafetyStatus(searchData= newCurrentTime, searchBy= "time")
            # realistically I should search by time. If the person searches via entry_id but they are not at the next entry then time is more acurate. It would basically have to update multiple times

    def _getNextChangeTime(self, entryID):
        row = self.dbHandler.getDataFromTable(tableName= "trackStatus", searchBy="entry_id", searchData= entryID + 1, attributeNameTuple=("time",), sessionID= self.currentSessionId)
        if(row != None):
            # next change time for track status
            return row[0]
        else:
            # no more trackStatus changes within the session
            return float("inf")
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
    # NOTE: Bug where on first load can't find any data for the newStatus
    def fetchSafetyStatus(self, searchData, searchBy):
        """_grabs data from the dbHandler and calls to set the safety status_
        NOTE: This should run checks and run getDataFromTable
        """
        #data needed from trackStatus Table
        columns = ("entry_id", "session_id", "time", "track_safety_status", "message")
        # fetch status from DB
        #creates a tuple to search through
        newStatus = self.dbHandler.getDataFromTable(tableName= "trackStatus", searchBy= searchBy, searchData= searchData, attributeNameTuple= columns, sessionID= self.currentSessionId)

        # ! newStatus being None is causing a CTD. This needs to be handled elegantly in the future.
        if newStatus is None:
            return None

        """

        NOTE: Believe the _getNextStatusChange fixes below issue
        # stub value need to wright a try except block for getting data from db
        #grab next change time from table status
        nextChangeTuple = self.dbHandler.getDataFromTable(tableName= "trackStatus", searchBy= "entry_id", searchData=newStatus[0] + 1, attributeNameTuple= ("time", ), sessionID= self.currentSessionId)

        
        if nextChangeTuple is None:
            return None
        """
        # set data to idle
        if(newStatus == None):
            self.setSafetyStatus("Idle")
            self.lastStatusChangeTime = 0.00
            # NOTE: find first index of session | write a function to find this 
            self.currentIndex = 0 # start fo session 
            self.nextStatusChangeTime = self._getNextChangeTime(self.currentIndex)
        else:
            #grab next change time from table status
            self.currentIndex = newStatus[0]
            self.nextStatusChangeTime = self._getNextChangeTime(self.currentIndex)
            self.lastStatusChangeTime = newStatus[2]
            self.setSafetyStatus(newStatus[4])
            self.currentIndex += self.currentIndex

    
    def fetchSurfaceStatus(self):
        # fetch status from DB
        # newStatus = dbHandler.getSafetyStatus()
        # stub value need to wright a try except block for getting data from db
        self.setSurfaceStatus("test")

