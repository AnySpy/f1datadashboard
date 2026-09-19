
"""
    
    ____________________________________________________________________________
    |                            track status table                            |
    ____________________________________________________________________________
    |entryID| session ID |time | track safety status code | track surface temp | 
    ____________________________________________________________________________
    |   0   |    1       | 0.00|              0           |        97.2        | example data
    ____________________________________________________________________________

       
"""

class DBhandler:
    def __init__(self):
        print("loading...")

    def sendData():
        return 0
    #might be able to estimate this based off of rainfall and driver comms 
    def getTrackSurfaceData(approxTime: float) -> dict:
        #search track table
        trackSurfaceData: dict = {"surfaceTemp": 0, "surfaceStatus": "dry"}
        return trackSurfaceData

    def getTrackSafetyStatus(approxTime: float) -> str:
        #search track table
        # we will pull the index of what is in this list for the actual readable warning code to send to the race simulation view model
        # stub need to actually make a list of statuses needed
        trackSafetyCodes: list = ("normal", "warning", "danger")
        # pull the int from the track table
        trackSafetyStatus: int = 0 

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

