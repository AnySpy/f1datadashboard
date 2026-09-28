# basic test application
from PySide6.QtCore import Signal,Qt
from UI.Theme import theme
<<<<<<< HEAD
from ViewModels.raceSimulationVM import TrackStatusVM, PlayControlsVM
from Services.dbhandler import DBhandler
=======
from ViewModels.raceSimulationVM import TrackStatusVM
>>>>>>> dde858130e92c019b3a831db0dd36d56f63cc7bb
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QSlider,
    QComboBox,
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
        """
        )


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
        # create an instance of the VM
        self.trackStatusVM = trackStatusVM
        # stub info while waiting for race to load
        self.message: str = "No Data Loaded..."
        # formating layout
        layout = QHBoxLayout(self)
        # create the label that will be updated
        self.statusLabel = QLabel(self.message)
        layout.addWidget(self.statusLabel)

        # connect to the VM
        self.trackStatusVM.updatedTrackSafety.connect(self.onStatusChange)

    def onStatusChange(self, status: str):
        print("status changed")
        print(status)
        self.message = status
        self.statusLabel.setText(self.message)

<<<<<<< HEAD
        
class PlayControlsUI(Card):
    def __init__(self, playControlsController: PlayControlsVM):
        super().__init__()
        self.playControlsVM = playControlsController
        layout = QVBoxLayout(self)
        #scrub bar
        scrub_row = QHBoxLayout()
        self.position_label = QLabel("00:00")
        self.scrub_slider = QSlider(Qt.Horizontal)
        self.scrub_slider.setRange(0, 100)  # will be rescaled once duration is known
        self.duration_label = QLabel("00:00")

        scrub_row.addWidget(self.position_label)
        scrub_row.addWidget(self.scrub_slider)
        scrub_row.addWidget(self.duration_label)
        layout.addLayout(scrub_row)

# on UI element change call viewModel.set{action} then have the set action updated a signal that the UI reads

    def onClickPlay():
        print("user clicked play/pause")

    def onSliderMoved():
        print("slider moved")
        # take time that slider displays then set the currentTime in the playControls VM

    def onPlaybackSpeedChanged():
        print("playback speed changed")
        #change playback speed
    def setRaceDuration():
        print("setting race duration")
        
=======

>>>>>>> dde858130e92c019b3a831db0dd36d56f63cc7bb
class HomePage(QWidget):
    def __init__(self, view_model: TrackStatusVM):
        super().__init__()
<<<<<<< HEAD
        self.monitorTrackStatus = TrackStatusVM(databaseManager)
        self.playControlsController = PlayControlsVM()
=======
        self.monitorTrackStatus = view_model
>>>>>>> dde858130e92c019b3a831db0dd36d56f63cc7bb
        # make a grid layout of 13x11ish
        # grid layout (rowstart, colstart, spanrows, spancols)
        gridLayout = QGridLayout(self)
        gridLayout.setSpacing(gridMargin)
        gridLayout.setSpacing(gridMargin)
        gridLayout.setContentsMargins(gridMargin, gridMargin, gridMargin, gridMargin)
<<<<<<< HEAD
        driverSimFrame = DriverSIM(trackStatus = self.monitorTrackStatus, playControlsController = self.playControlsController)
        gridLayout.addWidget(driverSimFrame, 1,0, 3, 3)
=======
        driverSimFrame = DriverSIM(trackStatus=self.monitorTrackStatus)
        gridLayout.addWidget(driverSimFrame, 1, 0, 3, 3)
>>>>>>> dde858130e92c019b3a831db0dd36d56f63cc7bb
        sessionFrame = SessionSelector()
        gridLayout.addWidget(sessionFrame, 0, 0, 1, 3)
        driverStandingsFrame = DriverStandings()
        gridLayout.addWidget(driverStandingsFrame, 0, 3, 4, 1)
        driverTelemetryCard1 = DriverTelemetry()
        gridLayout.addWidget(driverTelemetryCard1, 4, 0, 1, 4)
        driverTelemetryCard2 = DriverTelemetry()
        gridLayout.addWidget(driverTelemetryCard2, 5, 0, 1, 4)
        self.monitorTrackStatus.fetchSafetyStatus()


class DriverSIM(Card):
    def __init__(self, trackStatus: TrackStatusVM, playControlsController: PlayControlsVM):
        super().__init__()
        layout = QVBoxLayout(self)
        # create the track status card that will sit inside of the race sim
        self.trackStatusCard = TrackStatusCard(trackStatus)
        self.playControlsUI = PlayControlsUI(playControlsController)
        layout.addWidget(self.trackStatusCard)
        # this will hold the simulated race
        layout.addWidget(QLabel("Race Sim"))
        layout.addWidget(self.playControlsUI)


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
<<<<<<< HEAD
        self.yearSelector = QComboBox()
        self.sessionSelector = QComboBox()

        layout.addWidget(self.yearSelector)
        layout.addWidget(self.sessionSelector)

    def setAvailableYears():
        """
        grabs available years from fastf1 api call
        if sys.currentyear > most recent year in db then call fastf1 api to get new data
        """
        print("change years available for selection")
    def setAvailableSessions():
        """
        once yearSelector is chosen ask fastf1 api 
        """
        print("change sessions available for review")
        
=======
>>>>>>> dde858130e92c019b3a831db0dd36d56f63cc7bb
