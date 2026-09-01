from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout

"""
@brief page for the driver profiles
"""


class DriverProfiles(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Driver Profiles"))
