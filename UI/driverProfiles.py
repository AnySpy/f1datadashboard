from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt

"""
@brief page for the driver profiles
"""
class DriverProfiles(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Driver Profiles"))