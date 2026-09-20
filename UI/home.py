# basic test application
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
)

layoutColor: str = "#bd8c77"
gridMargin: int = 12
"""
@brief class holding the startup page that contains a grid layout of driver sim,
       driver standings, and driver telemetry, and track data
"""

class Card(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(
            f"""
                background-color: {layoutColor};
                border-radius: 12px;        
        """)

class HomePage(QWidget):
    def __init__(self):
        super().__init__()

        # make a grid layout of 13x11ish
        # grid layout (rowstart, colstart, spanrows, spancols)
        gridLayout = QGridLayout(self)
        gridLayout.setSpacing(gridMargin)
        gridLayout.setSpacing(gridMargin)
        gridLayout.setContentsMargins(gridMargin, gridMargin, gridMargin, gridMargin)
        driverSimFrame = DriverSIM()
        gridLayout.addWidget(driverSimFrame, 1,0, 3, 3)
        sessionFrame = SessionSelector()
        gridLayout.addWidget(sessionFrame, 0, 0, 1, 3)
        driverStandingsFrame = DriverStandings()
        gridLayout.addWidget(driverStandingsFrame, 0,3,4,1)
        driverTelemetryCard1 = DriverTelemetry()
        gridLayout.addWidget(driverTelemetryCard1, 4,0,1,4)
        driverTelemetryCard2 = DriverTelemetry()
        gridLayout.addWidget(driverTelemetryCard2, 5, 0, 1, 4)




"""
@brief driver simulation of the race
@notes this should take up the most space
"""



class DriverSIM(Card):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
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
        