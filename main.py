import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtWidgets import QHBoxLayout, QWidget, QVBoxLayout, QPushButton
from PySide6.QtGui import *

from UI.home import HomePage
from UI.dataAnalysisPage import DataAnalysisPage
from UI.driverProfiles import DriverProfiles



"""
Global Vars
"""
currentPageIndex = 0

"""
@brief This is is the class describing UI components of the main window
        launched on startup
"""
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("F1 Data Analysis")
        # set the main container
        mainContainer = QWidget()
        self.setCentralWidget(mainContainer)

        #make the layout horizontal
        mainContainerLayout = QHBoxLayout(mainContainer)

        # create the stack for the different pages
        self.stack = QStackedWidget()

        # create the main elements and pass down the switch page function
        self.sidebar = Sidebar(self.switch_page) # changed the 1st self to try to pass down currentPageIndx
        self.home = HomePage()
        self.settings = DataAnalysisPage()
        self.driverProfiles = DriverProfiles()

        # add the pages to the stack
        self.stack.addWidget(self.home)
        self.stack.addWidget(self.settings)
        self.stack.addWidget(self.driverProfiles)

        # add the sidebar and stack to the maincontainerlayout
        mainContainerLayout.addWidget(self.sidebar)
        mainContainerLayout.addWidget(self.stack)

    """
    @brief this function changes the current index of the stack to
           change the current widget being shown
    """ 
    def switch_page(self, index):
        self.stack.setCurrentIndex(index)

"""
@brief Create a sidebar menu that appears on the left side of the screen
@param utilize the QWidget super class to handle the initialization
@notes change the button creation, you are basically making the same button 
       over and over again just change to a function or smth
"""
class Sidebar(QWidget):
    def __init__(self, switch_page):
        super().__init__()
        self.setFixedWidth(125)
        #self.setMaximumWidth(150)
        #self.setMinimumWidth(40)
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.Base)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        changePageBtn = QPushButton("Home")
        # removes window auto focussing to this button on launch
        changePageBtn.setFocusPolicy(Qt.NoFocus)
        changePageBtn.clicked.connect(lambda: switch_page(0))
        layout.addWidget(changePageBtn)

        changePageBtn = QPushButton("Data Analysis")
        changePageBtn.setFocusPolicy(Qt.NoFocus)
        changePageBtn.clicked.connect(lambda: switch_page(1))
        layout.addWidget(changePageBtn)

        changePageBtn = QPushButton("Driver Profiles")
        changePageBtn.setFocusPolicy(Qt.NoFocus)
        changePageBtn.clicked.connect(lambda: switch_page(2))
        layout.addWidget(changePageBtn)


    """
    @brief styling function to add a background color to current page
    """
    def updateHightlight(self):
        print("update button highlight")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(700, 300)
    window.show()
    sys.exit(app.exec())