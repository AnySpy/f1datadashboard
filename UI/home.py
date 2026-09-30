# basic test application
from PySide6.QtCore import Signal,Qt
from UI.Theme import theme
from ViewModels.raceSimulationVM import PlayControlsVM
from ViewModels.trackStatusVM import TrackStatusVM
from Services.dbhandler import DBhandler
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


class PlayControlsUI(Card):
    def __init__(self, playControlsController: PlayControlsVM):
        super().__init__()
        self.playControlsVM = playControlsController
        self.raceDuration: float = 0.00
        self.formattedTime: str = "00:00:00"

        #connect on duration change to the playControlsVM
        self.playControlsVM.updatedRaceDuration.connect(self.onDurationChange)
        self.playControlsVM.updatedTime.connect(self.onCurrentTimeChange)
        layout = QVBoxLayout(self)
        #scrub bar
        scrubRow = QHBoxLayout()
        self.currentTimeLabel = QLabel("00:00")
        # ? I had to change this to Qt.Orientation.Horizontal to get it to compile for some reason. Apparently it's a newer change with PySide6?
        # create the slider NOTE: might want to make this it's own class later on
        self.scrubSlider = QSlider(Qt.Orientation.Horizontal)
        self.scrubSlider.setRange(0, 100)  # will be rescaled once duration is known
        self.durationLabel = QLabel(self.formattedTime)
        # set the signal changes
        self.scrubSlider.valueChanged.connect(self._onSliderValueChanged)
        self.scrubSlider.sliderPressed.connect(self._onSliderPressed)
        self.scrubSlider.sliderReleased.connect(self._onSliderReleased)
        # is slider being messed with 
        self.sliderInUse: bool = False

        scrubRow.addWidget(self.currentTimeLabel)
        scrubRow.addWidget(self.scrubSlider)
        scrubRow.addWidget(self.durationLabel)
        layout.addLayout(scrubRow)

# on UI element change call viewModel.set{action} then have the set action updated a signal that the UI reads

    def onClickPlay():
        print("user clicked play/pause")

    def _onSliderPressed(self):
        # stop the slider from updating from currentTime changing
        self.playControlsVM.timer.blockSignals(True)
        self.sliderInUse = True
    def _onSliderReleased(self):
        # allow the slider to update from currentTime changing
        self.playControlsVM.timer.blockSignals(False)
        self.sliderInUse = False
    def _onSliderValueChanged(self):
        print("slider moved")
        # take time that slider displays then set the currentTime in the playControls VM
        self.playControlsVM.setCurrentTime(self.scrubSlider.value())

    def onPlaybackSpeedChanged():
        print("playback speed changed")
        #change playback speed

    def _formatTime(self, totalSeconds: float):
        totalSeconds = int(round(totalSeconds))
        hours = totalSeconds // 3600
        minutes = (totalSeconds % 3600) // 60
        seconds = totalSeconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
   
    def onCurrentTimeChange(self, newCurrentTime):
        #self.scrubSlider.blockSignals(True)
        time = self._formatTime(newCurrentTime)
        self.currentTimeLabel.setText(time)
        #self.scrubSlider.blockSignals(False)
        # update slider if not being dragged
   
    def onDurationChange(self, newDuration):
        #self.scrubSlider.blockSignals(True)
        self.raceDuration = newDuration
        self.formattedTime = self._formatTime(newDuration)
        self.scrubSlider.setRange(0, int(self.raceDuration))
        self.durationLabel.setText(self.formattedTime)
        #self.scrubSlider.blockSignals(False)

class HomePage(QWidget):
    def __init__(self, trackStatusViewModel: TrackStatusVM, playControlsViewModel):
        super().__init__()
        self.monitorTrackStatus = trackStatusViewModel
        self.playControlsController = playControlsViewModel
        self.currentSessionID = 1
        
        # make a grid layout of 13x11ish
        # grid layout (rowstart, colstart, spanrows, spancols)
        gridLayout = QGridLayout(self)
        gridLayout.setSpacing(gridMargin)
        gridLayout.setSpacing(gridMargin)
        gridLayout.setContentsMargins(gridMargin, gridMargin, gridMargin, gridMargin)
        driverSimFrame = DriverSIM(trackStatus = self.monitorTrackStatus, playControlsController = self.playControlsController)
        gridLayout.addWidget(driverSimFrame, 1,0, 3, 3)
        sessionFrame = SessionSelector()
        gridLayout.addWidget(sessionFrame, 0, 0, 1, 3)
        driverStandingsFrame = DriverStandings()
        gridLayout.addWidget(driverStandingsFrame, 0, 3, 4, 1)
        driverTelemetryCard1 = DriverTelemetry()
        gridLayout.addWidget(driverTelemetryCard1, 4, 0, 1, 4)
        driverTelemetryCard2 = DriverTelemetry()
        gridLayout.addWidget(driverTelemetryCard2, 5, 0, 1, 4)
        self.monitorTrackStatus.fetchSafetyStatus(searchData= 1, searchBy="entry_id")
        self.playControlsController.fetchRaceDuration(self.currentSessionID)


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
        