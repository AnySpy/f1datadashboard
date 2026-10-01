import sqlite3
from Services import database
from fastf1.events import Session

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
# Tables/columns the handler is allowed to query. Table and column names
# can't be passed as "?" parameters in SQLite, so they get built into the
# query string -- this whitelist makes sure only known names ever get there.
ALLOWED_COLUMNS: dict = {
    "sessions": {"session_id", "year", "event_name", "session_type", "total_laps", "total_time"},
    "laps": {
        "lap_id",
        "session_id",
        "driver",
        "team",
        "lap_number",
        "lap_time_seconds",
        "compound",
        "tyre_life",
        "track_status",
        "is_pit_lap",
        "position",
    },
    "drivers": {"session_id", "driver_code", "full_name", "team", "number", "color"},
    "weather": {
        "weather_id",
        "session_id",
        "air_temp",
        "track_temp",
        "humidity",
        "rainfall",
        "sample_time",
    },
    "trackStatus": {"entry_id", "session_id", "time", "track_safety_status", "message"},
    "results": {
        "session_id",
        "driver_code",
        "grid_position",
        "finish_position",
        "classified_position",
        "points",
        "status",
    },
}

# Tables that have a numeric elapsed-time column (seconds) we can search by.
TIME_COLUMN: dict = {
    "trackStatus": "time",
}

# What the app should show before the first recorded status change.
DEFAULT_TRACK_STATUS: dict = {
    "entry_id": -1,
    "time": 0.0,
    "statusCode": 1,
    "message": "AllClear",
}


class DBhandler:
    def __init__(self):
        print("loading...")
        database.create_schema()
        self.conn = sqlite3.connect(database.DB_PATH)

    def close(self) -> None:
        """closes the database connection"""
        self.conn.close()

    def getKnownDrivers(self) -> dict[str, str]:
        """Returns a list of every driver that has been recorded in the database

        Returns:
            dict[str, str]: A dictionary containing the driver code (e.g. VER) as the key and the driver's full name (e.g. Max Verstappen) as the value.
        """
        cursor = self.conn.cursor()

        cursor.execute(
            "SELECT DISTINCT driver_code, full_name FROM drivers WHERE driver_code IS NOT NULL"
        )

        rows = cursor.fetchall()

        return {code: name for code, name in rows}

    # might be able to estimate this based off of rainfall and driver comms
    def getTrackSurfaceData(self, approxTime: float) -> dict:
        # search track table
        trackSurfaceData: dict = {"surfaceTemp": 0, "surfaceStatus": "dry"}
        return trackSurfaceData

    def _checkNames(self, tableName: str, columns: tuple) -> None:
        """
        _summary_: makes sure the table and every column are in ALLOWED_COLUMNS
                   before they get put into a query string (stops SQL injection
                   through table/column names)

        Raises:
            ValueError: if the table or any column isn't allowed
        """
        if tableName not in ALLOWED_COLUMNS:
            raise ValueError(f"unknown table: {tableName}")
        for column in columns:
            if column not in ALLOWED_COLUMNS[tableName]:
                raise ValueError(f"unknown column '{column}' for table {tableName}")
        print("dbhandler.py/_checkNames: Valid access to tables within database")

    # NOTE: Flagged for Depreciation
    def getSessionID(self, tableName: str, searchIndex: int) -> int:
        """
        _summary_: get the session_id of one row, looked up by entry_id

        Returns:
            _type_ int: the session_id, or -1 if the row doesn't exist
        """
        self._checkNames(tableName, ("entry_id", "session_id"))
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT session_id FROM {tableName} WHERE entry_id = ? LIMIT 1",
            (searchIndex,),
        )
        sessionID = cursor.fetchone()
        if sessionID is None:
            print("session_id could not be found\n")
            return -1
        # fetchone() returns a tuple like (1,) -- return the number inside it
        return sessionID[0]

    def _calculateTotalSessionTime(self, session: Session) -> float:
        """ 
        Args:
            session_id (int): _session id of race to calculate total time_

        Returns:
            float: _returns the total race duration_
        """

        """Time | pd.Timedelta | The drivers total race time 
        (values only given if session is ‘Race’, ‘Sprint’, ‘Sprint Shootout’ or 
        ‘Sprint Qualifying’ >and the driver was not more than one lap behind 
        the leader"""
        # can I just pass the memory location so I don't have to load it again
        # this makes a new DF
        newSessionStatus = session.session_status
        startFlag = newSessionStatus.loc[newSessionStatus["Status"] == "Started", "Time"].iloc[0]
        endFlag = newSessionStatus.loc[newSessionStatus["Status"] == "Finished", "Time"].iloc[-1]
        raceDuration = (endFlag - startFlag).total_seconds()
        print(f"{session.name} total session time = {raceDuration}")
        return raceDuration
    
    def _setSessionTotalTime(self):
        """
        _This function needs to be able to set if not set each session time in the session table with the proper session time_
        """
        print("setting total time of sessions")
    def getSessionTime(self, session_id: int) -> float | None:
        """_summary_ sends the race duration of specified session to the playControlsVM

        Args:
            session_id (int): _this is the race session that you are trying to search for_

        Returns:
            _float_: _returns a float value that is the race duration in seconds_
        """
        sessionTime: float
        # testing print statement
        print(f"dbhandler.py/getSessionTime: attempting to find session time at session{session_id}")
        sessionDF = self.getDataFromTable(tableName= "sessions", searchBy = "first_entry", searchData= session_id, attributeNameTuple= ("total_time",), sessionID= session_id)

        # ! sessionDF being None is causing a CTD. This should be handled elegantly in the future.
        if sessionDF is None:
            return None

        # convert DF to float | just take the first value from the tuple
        sessionTime: float = sessionDF[0]
        return sessionTime
    
    def getDataFromTable(
        self,
        tableName: str,
        searchBy: str,
        searchData: int | float,
        attributeNameTuple: tuple,
        sessionID: int | None = None,
    ) -> tuple | None:
        """
        _summary_: function to get data from database tables

        NOTE:
            - added 2 ways to search because if we skipback the playcontrols then the endflag will no longer be correct
            - searching by time returns the NEAREST ENTRY AT OR BEFORE approxTime
              (the last known state at that moment), never a future entry.
              Because it only depends on approxTime, skipping back/forward on
              the play controls just works -- no stored index to go stale.
        Args:
            tableName (str): the name of the table being accessed
            searchBy (str): the manner of which you are searching entry_id | time | first_entry
            searchData (int): the index of row needed | the approxtime of data
            attributeNameTuple (tuple): attributes needed to be returned
            sessionID (int): required when searchBy == "time" -- times restart
                             at 0 for every session, so we must know which race

        Returns:
            _type_ tuple: returns a tuple of data if found
            _type_ None: returns datatype None if no data was found from query

        Raises:
            ValueError: unknown table/column, or time search without a sessionID
        """
        self._checkNames(tableName, attributeNameTuple)
        # join the tuple to one string
        attributes = ", ".join(attributeNameTuple)
        print(f"dbhandler.py/_getDataFromTable: from {tableName} grab {attributes}")
        cursor = self.conn.cursor()

        if searchBy == "time":
            timeColumn = TIME_COLUMN.get(tableName)
            if timeColumn is None:
                raise ValueError(f"table {tableName} can't be searched by time")
            if sessionID is None:
                raise ValueError("sessionID is required when searching by time")
            dbQuery = (
                f"SELECT {attributes} FROM {tableName} "
                f"WHERE session_id = ? AND {timeColumn} <= ? "
                f"ORDER BY {timeColumn} DESC, entry_id DESC LIMIT 1"
            )
            cursor.execute(dbQuery, (sessionID, float(searchData)))
        elif(searchBy == "entry_id"):
            dbQuery = (
                f"SELECT {attributes} FROM {tableName} WHERE {searchBy} = ? LIMIT 1"
            )
            cursor.execute(dbQuery, (searchData,))
        elif(searchBy == "first_entry"):
            # search by first row that returns for specified session_id NOTE find another attribute to order by
            dbQuery = (
                f"SELECT {attributes} FROM {tableName} WHERE session_id = ? ORDER BY session_id LIMIT 1"
            )
            cursor.execute(dbQuery, (searchData,))

        results = cursor.fetchone()
        if results is None:
            print(f"dbhandler.py/getDataFromTable: No data found for {attributes} at {searchBy}: {searchData} within {tableName}")
            return None
        # return data from dbQuery to the function that needs it
        # NOTE: might be nice to return a dictionary so that it is easier to read from
        return results

    # NOTE: Flagged for depreciation once moved to trackStatusVM
    def _getNextStatusChange(
        self, sessionID: int, entryID: int, time: float
    ) -> float | None:
        """
        _summary_: finds when the NEXT track status change happens in this session

        Returns:
            _type_ float: time (seconds) of the next change
            _type_ None: there are no more changes -> this is the last one (endFlag)
        """
        cursor = self.conn.cursor()
        print(f"dbhandler.py/_getNextStatusChange: attempting to get the time at which the next status change happens within session {sessionID}")
        cursor.execute(
            """
            SELECT time FROM trackStatus
            WHERE session_id = ?
              AND (time > ? OR (time = ? AND entry_id > ?))
            ORDER BY time ASC, entry_id ASC
            LIMIT 1
            """,
            (sessionID, time, time, entryID),
        )
        nextRow = cursor.fetchone()
        print(f"data found: {nextRow}")
        return None if nextRow is None else nextRow[0]

    # NOTE: flagged for depreciation once validation checks are moved to trackStatusVM
    def getTrackSafetyStatus(
        self,
        approxTime: float = 0.00,
        currentSessionID: int = 1,
        currentIndex: int = -1,
        endFlag: bool = False,
    ) -> dict:
        """
        _summary_: get track data from db and return it to the track status view model

        Args:
            approxTime (float): the approximate time (seconds into the session) of the data for which you are looking
            currentSessionID (int): which session you are grabbing data for
            currentIndex (int): entry_id to grab directly; leave as -1 to search by approxTime
            endFlag (bool): kept for compatibility -- it is now worked out here, not passed in

        Returns:
            _type_ dict: {"entry_id", "time", "statusCode", "message",
                          "endFlag", "nextChangeTime"}
                endFlag is True when there are no more status changes after this one.
                nextChangeTime is when the VM needs to ask again (None at the end).
        """
        columns = ("entry_id", "session_id", "time", "track_safety_status", "message")
        trackTableData: tuple | None
        if currentIndex == -1:
            # pull data via approxTime (nearest entry at or before it)
            trackTableData = self.getDataFromTable(
                tableName="trackStatus",
                searchBy="time",
                searchData=approxTime,
                attributeNameTuple=columns,
                sessionID=currentSessionID,
            )
        else:
            # pull data via entry_id
            trackTableData = self.getDataFromTable(
                tableName="trackStatus",
                searchBy="entry_id",
                searchData=currentIndex,
                attributeNameTuple=columns,
            )
            if trackTableData is not None and trackTableData[1] != currentSessionID:
                print( f"entry {currentIndex} belongs to session {trackTableData[1]}, not {currentSessionID}")
                trackTableData = None

        if trackTableData is None:
            # before the first recorded change (or bad index): report a clear track
            trackStatusData = dict(DEFAULT_TRACK_STATUS)
            firstChange = self._getNextStatusChange(currentSessionID, -1, float("-inf"))
            trackStatusData["endFlag"] = firstChange is None
            trackStatusData["nextChangeTime"] = firstChange
            return trackStatusData

        entryID, _, time, statusCode, message = trackTableData
        nextChangeTime: float | None = self._getNextStatusChange(currentSessionID, entryID, time)
        # set trackStatusData to send to trackStatusVM
        trackStatusData: dict = {
            "entry_id": entryID,
            "time": time,
            "statusCode": statusCode,
            "message": message,
            "endFlag": nextChangeTime is None,
            "nextChangeTime": nextChangeTime,
        }
        print(f"dbhandler.py/DBhandler/getTrackSafetyStatus: nextChangeTime in trackStatusData: {trackStatusData['nextChangeTime']}")
        return trackStatusData

    """
                                driver table
    ______________________________________________________________________
    time | driver name | lap number |  |  
    ______________________________________________________________________
    0.00 |         0         |       97.2       |         "dry"          | 
    ______________________________________________________________________

    """

    def getDriverSpeed(self, approxTime: float, driverCode: str = "") -> float:
        # stub -- needs a telemetry (speed) table first; takes a driverCode
        # because speed is different for every driver
        return 0.00


def main():
    return 0


if __name__ == "__main__":
    main()
