from PySide6.QtCore import QObject, Signal

class PlayControlsViewModel(QObject):
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
    """
    def __init__(self):
        super().__init__()

    def togglePlay(self):
        #stub
        return 0 
    def currentTime(self):
        #stub
        return 0
    def scrubPlay(self):
        #stub
        return 0
    
    
