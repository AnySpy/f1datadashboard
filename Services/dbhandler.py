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
# Tables/columns the handler is allowed to query. Table and column names
# can't be passed as "?" parameters in SQLite, so they get built into the
# query string -- this whitelist makes sure only known names ever get there.
ALLOWED_COLUMNS: dict = {
    "sessions": {"session_id", "year", "event_name", "session_type", "total_laps"},
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
        self.conn = sqlite3.connect(DB_PATH)

    def close(self) -> None:
        """closes the database connection"""
        self.conn.close()

    def getKnownDrivers(self):
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
            print(redColor + "session_id could not be found" + resetColor + "\n")
            return -1
        # fetchone() returns a tuple like (1,) -- return the number inside it
        return sessionID[0]

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
            searchBy (str): the manner of which you are searching entry_id | time
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
        else:
            self._checkNames(tableName, (searchBy,))
            dbQuery = (
                f"SELECT {attributes} FROM {tableName} WHERE {searchBy} = ? LIMIT 1"
            )
            cursor.execute(dbQuery, (searchData,))

        results = cursor.fetchone()
        if results is None:
            print(f"No data found at {searchData}")
            return None
        # return data from dbQuery to the function that needs it
        return results

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
        return None if nextRow is None else nextRow[0]

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
                print(
                    redColor
                    + f"entry {currentIndex} belongs to session {trackTableData[1]}, not {currentSessionID}"
                    + resetColor
                )
                trackTableData = None

        if trackTableData is None:
            # before the first recorded change (or bad index): report a clear track
            trackStatusData = dict(DEFAULT_TRACK_STATUS)
            firstChange = self._getNextStatusChange(currentSessionID, -1, float("-inf"))
            trackStatusData["endFlag"] = firstChange is None
            trackStatusData["nextChangeTime"] = firstChange
            return trackStatusData

        entryID, _, time, statusCode, message = trackTableData
        nextChangeTime = self._getNextStatusChange(currentSessionID, entryID, time)

        # set trackStatusData to send to trackStatusVM
        trackStatusData: dict = {
            "entry_id": entryID,
            "time": time,
            "statusCode": statusCode,
            "message": message,
            "endFlag": nextChangeTime is None,
            "nextChangeTime": nextChangeTime,
        }
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
