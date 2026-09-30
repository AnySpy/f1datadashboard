from PySide6.QtCore import QObject, Signal, QTimer
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
    __updatedTrackSafety = Signal(str)  # normal, yellow flag, red flag
    __updatedTrackSurface = Signal(str)  # normal, damp, hot, etc.

    @property
    def updatedTrackSafety(self):
        return self.__updatedTrackSafety

    @property
    def updatedTrackSurface(self):
        return self.__updatedTrackSurface

    def __init__(self, playControlsVM: PlayControlsVM):
        super().__init__()
        # on init set Signals and class vars to normal
        self.currentTrackSafety = "normal"
        self.currentTrackSurface = "normal"
        self.currentIndex = 1
        self.currentSessionId: int = 1
        # NOTE: flagged for depreciation once playcontrolsVM updates all viewModels
        self.currentTime: float = 0.00
        self.lastStatusChangeTime: float | None = 0.0
        self.nextStatusChangeTime: float | None = 0.0
        self.playControlsVM = playControlsVM
        self.playControlsVM.updatedTime.connect(self._onCurrentTimeChange)
        # self.updatedTrackSurface.emit(self.currentTrackSurface)
        # self.updatedTrackSafety.emit(self.currentTrackSafety)
        # create a new DBhandler for fetching track info
        """
            NOTE: Read only
        """
        self.dbHandler = DBhandler()
        # fetch status codes from DB on creation

    def _onCurrentTimeChange(self, newCurrentTime):
        print(f"trackStatusVM.py/TrackStatusVM/_onCurrentTimeChange: Received Signal from playControlsVM updatedTime: {newCurrentTime}, nextStatusChangeTime: {self.nextStatusChangeTime}")
        # if newCurrentTime < self.lastStatusChangeTime then the scrubber has been used to go back in time
        if(newCurrentTime < self.lastStatusChangeTime):
            # fetch safety status based off of time
            self.fetchSafetyStatus(searchData= newCurrentTime, searchBy= "time")
        if(newCurrentTime >= self.nextStatusChangeTime):
            # fetch based off of index need to search based off of index prob not entry_id
            # ? NOTE: if we delete sessions from the db to alow users to save space this will prob need to change to reflect indexes not entry_id
            self.fetchSafetyStatus(searchData= self.currentIndex, searchBy="entry_id")

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
    def fetchSafetyStatus(self, searchData, searchBy):
        """_grabs data from the dbHandler and calls to set the safety status_
        NOTE: This should run checks and run getDataFromTable
        """
        #data needed from trackStatus Table
        columns = ("entry_id", "session_id", "time", "track_safety_status", "message")
        # fetch status from DB
        """
        newStatus = self.dbHandler.getTrackSafetyStatus(
            approxTime= self.currentTime, currentSessionID= self.currentSessionId, currentIndex = self.currentIndex, endFlag=False
        )
        """
        #creates a tuple to search through
        print(f"trackStatusVM.py/TrackStatusVM/fetchSafetyStatus trying to fetch track status from db")
        newStatus = self.dbHandler.getDataFromTable(tableName= "trackStatus", searchBy= searchBy, searchData= searchData, attributeNameTuple= columns, sessionID= self.currentSessionId)

        # ! newStatus being None is causing a CTD. This needs to be handled elegantly in the future.
        if newStatus is None:
            return None
        
        # stub value need to wright a try except block for getting data from db
        #grab next change time from table status
        nextChangeTuple = self.dbHandler.getDataFromTable(tableName= "trackStatus", searchBy= "entry_id", searchData=newStatus[0] + 1, attributeNameTuple= ("time", ), sessionID= self.currentSessionId)

        if nextChangeTuple is None:
            return None
        
        print(f"trackStatusVM.py/TrackStatusVM/fetchSafetyStatus: newStatus: {newStatus}, nextChangeTuple: {nextChangeTuple}")
        self.lastStatusChangeTime = newStatus[2]
        self.nextStatusChangeTime = nextChangeTuple[0]
        self.setSafetyStatus(newStatus[4])
        self.currentIndex += self.currentIndex

    
    def fetchSurfaceStatus(self):
        # fetch status from DB
        # newStatus = dbHandler.getSafetyStatus()
        # stub value need to wright a try except block for getting data from db
        self.setSurfaceStatus("test")

