# basic test application
from PySide6.QtWidgets import QGridLayout, QApplication, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QFrame
from PySide6.QtCore import Qt

"""
@brief class holding the startup page that contains a grid layout of driver sim,
       driver standings, and driver telemetry, and track data
"""
class HomePage(QWidget):

    def __init__(self):
        super().__init__()

        #make a grid layout of 13x11ish
        layout = QGridLayout(self)
        layout.addWidget(QLabel("Home Page"))



"""
@brief driver simulation of the race
@notes this should take up the most space
"""
class DriverSIM(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        container = QFrame()
        container.resize(100,100)
        container.setStyleSheet("background-color: red")
        layout.addWidget(container)

class DriverStandings(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Driver Standings"))


class DriverTelemetry(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.addWidget(QLabel("Driver Telemetry"))