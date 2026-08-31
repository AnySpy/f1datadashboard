from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

"""
@brief page for data analysis
"""
class DataAnalysisPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Data Analysis"))