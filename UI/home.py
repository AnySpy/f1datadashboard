# basic test application
from PySide6.QtCore import Signal
from UI.Theme import theme
from ViewModels.raceSimulationVM import TrackStatusVM
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
)

layoutColor: str = theme.info
gridMargin: int = 12

"""
    TODO: 
    - write documentation for each class
"""
class Card(QFrame):
    """_summary_

    Args:
        QFrame (QWidget): _generates a basic layout for each other card_
    """
    def __init__(self):
        super().__init__()
        self.setStyleSheet(
            f"""
                background-color: {layoutColor};
                border-radius: 12px;        
        """)

class DriverCard(QFrame):
    def __init__(self, driverName, currentPlacement):
        super().__init__()

class TrackStatusCard(Card):
    """_creates a card that shows updated data from the VM_

    Args:
        Card (QFrame): _description_
    """    
    def __init__(self, trackStatusVM: TrackStatusVM):
        super().__init__()
        self.setStyleSheet(f"""background-color: {theme.background}""")
        #create an instance of the VM
        self.trackStatusVM = trackStatusVM
        #stub info while waiting for race to load
        self.message: str = "No Data Loaded..."
        #formating layout
        layout = QHBoxLayout(self)
        #create the label that will be updated
        self.statusLabel = QLabel(self.message)
        layout.addWidget(self.statusLabel)

        #connect to the VM
        self.trackStatusVM.updatedTrackSafety.connect(self.onStatusChange)


    def onStatusChange(self, status:str):
        print("status changed")
        print(status)
        self.message = status
        self.statusLabel.setText(self.message)

        

        
class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.monitorTrackStatus = TrackStatusVM()
        # make a grid layout of 13x11ish
        # grid layout (rowstart, colstart, spanrows, spancols)
        gridLayout = QGridLayout(self)
        gridLayout.setSpacing(gridMargin)
        gridLayout.setSpacing(gridMargin)
        gridLayout.setContentsMargins(gridMargin, gridMargin, gridMargin, gridMargin)
        driverSimFrame = DriverSIM(trackStatus = self.monitorTrackStatus)
        gridLayout.addWidget(driverSimFrame, 1,0, 3, 3)
        sessionFrame = SessionSelector()
        gridLayout.addWidget(sessionFrame, 0, 0, 1, 3)
        driverStandingsFrame = DriverStandings()
        gridLayout.addWidget(driverStandingsFrame, 0,3,4,1)
        driverTelemetryCard1 = DriverTelemetry()
        gridLayout.addWidget(driverTelemetryCard1, 4,0,1,4)
        driverTelemetryCard2 = DriverTelemetry()
        gridLayout.addWidget(driverTelemetryCard2, 5, 0, 1, 4)
        self.monitorTrackStatus.fetchSafetyStatus()


class DriverSIM(Card):
    def __init__(self, trackStatus: TrackStatusVM):
        super().__init__()
        layout = QVBoxLayout(self)
        #create the track status card that will sit inside of the race sim
        self.trackStatusCard = TrackStatusCard(trackStatus)
        layout.addWidget(self.trackStatusCard)
        # this will hold the simulated race
        layout.addWidget(QLabel("Race Sim"))


class DriverStandings(Card):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Driver Standings"))
        

class DriverTelemetry(Card):
    def __init__(self):
        super().__init__()
        self.setMaximumHeight(100)
        layout = QHBoxLayout(self)
        layout.addWidget(QLabel("Driver Telemetry"))

class SessionSelector(Card):
    def __init__(self):
        super().__init__()
        self.setMaximumHeight(50)
        layout = QHBoxLayout(self)
        layout.addWidget(QLabel("SessionSelector"))
        