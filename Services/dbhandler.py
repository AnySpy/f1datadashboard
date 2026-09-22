import sqlite3
from Services.database import DB_PATH
from tests.SignalTesting import redColor, resetColor
from Services import database
"""
    SCHEMA:
    _________________________________________________________________
    |                            track status table        |        |
    _________________________________________________________________
    |entry_id| session_id |time | track_safety_status      | message|
    _________________________________________________________________
    |   0    |     1      | 000 |              0           | normal |example data
    _________________________________________________________________

    NOTE: This table tracks each time the status has been changed not on a time basis.
          It doesn't update every {number} seconds like other tables. 

    track status codes as defined by Fastf1 api:
        '1': Track clear (beginning of session or to indicate the end
           of another status)
        - '2': Yellow flag (sectors are unknown)
        - '3': ??? Never seen so far, does not exist?
        - '4': Safety Car
        - '5': Red Flag
        - '6': Virtual Safety Car deployed
        - '7': Virtual Safety Car ending (As indicated on the drivers steering wheel, on tv and so on; status '1'
          will mark the actual end)
"""
class DBhandler:
    def __init__(self):
        print("loading...")
        database.create_schema()
        self.conn = sqlite3.connect(DB_PATH)
        #might be able to estimate this based off of rainfall and driver comms 
    def getTrackSurfaceData(self, approxTime: float) -> dict:
        #search track table
        trackSurfaceData: dict = {"surfaceTemp": 0, "surfaceStatus": "dry"}
        return trackSurfaceData

    def getSessionID(self, tableName: str, searchIndex: int):
        cursor = self.conn.cursor()
        cursor.execute
        ("""
        SELECT session_id
        FROM ?
        WHERE entry_id = ?
        LIMIT 1
        """),
        (tableName, searchIndex)
        sessionID = cursor.fetchone()
        if(sessionID is None):
            print( redColor + "session_id could not be found" + resetColor + "\n")
            return -1
        else:
            return sessionID

    def getDataFromTable(self, tableName: str, searchBy: str ,searchData: int | float, attributeNameTuple: tuple) -> tuple | None:
        """ 
        _summary_: function to get data from database tables

        NOTE:
            - added 2 ways to search because if we skipback the playcontrols then the endflag will no longer be correct
        Args:
            tableName (str): the name of the table being accessed
            searchBy (str): the manner of which you are searching entry_id | time
            searchData (int): the index of row needed | the approxtime of data
            attributeNameList (list): list of attributes needed to be returned

        Returns:
            _type_ tuple: returns a tuple of data if found
            _type_ None: returns datatype None if no data was found from query

        TODO:
            - this is dangerous for cross site scripting need to insure that we run type checks and handle errors without program chrashing
        """
        # join the list to one string
        attributes = ", ".join(attributeNameTuple)
        dbQuery = f"SELECT {attributes} FROM {tableName} WHERE {searchBy} = ? LIMIT 1"
        cursor = self.conn.cursor()
        cursor.execute(dbQuery , (searchData, ))
        results = cursor.fetchone()
        if(results is None):
            print(f"No data found at {searchData}")
            return None
        else:
            #return data from dbQuery to the function that needs it
            return results
         

    def getTrackSafetyStatus(self, approxTime: float = 0.00, currentSessionID: int = 1, currentIndex: int = -1, endFlag: bool = False) -> dict:
        """
        _summary_: get track data from db and return it to the track status view model 

        Args:
            approxTime (float): the approximate time of the data for which you are looking
            currentSessionID (int): which session you are grabbing data for
            currentIndex (int): the index of which you are grabbing data from
            endFlag (bool): flag to determine if there are no other status changes for the current session

        Returns:
            _type_ dict: searchable dictionary of track status data
        """
        #search track table
        # we will pull the index of what is in this list for the actual readable warning code to send to the race simulation view model
        # stub need to actually make a list of statuses needed
        trackTableData: tuple
        if(currentIndex == -1):
            # pull data via entry_id
            print("searching db via approx time")
            trackTableData = self.getDataFromTable(tableName= "trackStatus", searchBy= "time", searchData= approxTime, attributeNameTuple= ("entry_id", "time", "track_safety_status", "message"))
        elif(approxTime == 0.00):
            print("searching db via index")
            trackTableData = self.getDataFromTable(tableName= "trackStatus", searchBy= "entry_id", searchData= currentIndex, attributeNameTuple= ("entry_id", "time", "track_safety_status", "message"))
            #pull data via approxTime
        
        if(self.getDataFromTable(tableName = "trackStatus", searchBy= "entry_id", searchData= currentIndex + 1, attributeNameTuple= ("session_id",)) != currentSessionID):
            endFlag = True
            print("SET END FLAG")
        
        trackStatusData: dict = {"entry_id" : int, "time": float, "statusCode" : int, "message" : str, "endFlag": endFlag}
        
        # set trackStatusData to send to trackStatusVM
        trackStatusData["entry_id"] = trackTableData[0]
        trackStatusData["time"] = trackTableData[1]
        trackStatusData["statusCode"] = trackTableData[2]
        trackStatusData["message"] = trackTableData[3]
        trackStatusData["endFlag"] = endFlag
        print(trackStatusData)
        return trackStatusData

    
    """
                                driver table
    ______________________________________________________________________
    time | driver name | lap number |  |  
    ______________________________________________________________________
    0.00 |         0         |       97.2       |         "dry"          | 
    ______________________________________________________________________

    """
    def getDriverSpeed(approxTime: float) -> float:
        return 0.00


def main():
    return 0

if __name__ == "__main__":
    main()