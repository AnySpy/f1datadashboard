from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from Services.dbhandler import DBhandler

"""
@brief page for data analysis
"""


class DataAnalysisPage(QWidget):
    def __init__(self ,dbHandler: DBhandler):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Data Analysis"))
