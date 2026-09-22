from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QSizePolicy, QScrollArea, QGridLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QPainterPath
from ViewModels.driverProfilesVM import DriverProfilesViewModel
import typing

"""
@brief page for the driver profiles
"""

class DriverProfiles(QWidget):
    def __init__(self):
        super().__init__()
        self.view_model = DriverProfilesViewModel()

        grid = QGridLayout(self)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(0)

        self.nav_bar = DriverNavBar()
        grid.addWidget(self.nav_bar, 0, 0, 1, 2)

        self.driver_about_section = DriverAboutSection()
        grid.addWidget(self.driver_about_section, 1, 0)

        self.driver_stats_section = DriverStatsSection(self.view_model)
        grid.addWidget(self.driver_stats_section, 1, 1)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

# Top nav bar. This should probably be a search bar in hindsight, but I like the design of this right now so we're going with it.
class DriverNavBar(QWidget):
    def __init__(self):
        super().__init__()

        # TODO: We should automatically pull all of this from the database before looping through it eventually.
        drivers = ["ME", "VER", "HAM", "RUS", "NOR", "LAW", "LEC"]

        layout = QVBoxLayout(self)
        driver_container = QHBoxLayout()

        driver_labels = QLabel("Drivers")
        vertical_line = QFrame(frameShape=QFrame.Shape.VLine)
        horizontal_line = QFrame(frameShape=QFrame.Shape.HLine)

        vertical_line.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        driver_container.addWidget(driver_labels)
        driver_container.addWidget(vertical_line)

        for driver in drivers:
            driver_button = QPushButton(driver)
            driver_container.addWidget(driver_button)

        driver_container.setContentsMargins(0, 0, 0, 0)
        driver_container.setSpacing(10)

        layout.addLayout(driver_container)
        layout.addWidget(horizontal_line)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

# Left side, contains a picture, the name of the driver, and their biography
class DriverAboutSection(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        basic_info = QVBoxLayout()
        bio = QVBoxLayout()

        # TODO: All of this is a placeholder and needs to be pulled from somewhere instead of being hardcoded.

        # ? The idea is that we scale the image down to 100x100, create a canvas object of the same size, 
        # ?     create a painter object with a circular path that then paints the image as a circle onto the canvas,
        # ?     and then creates a label holder for that image to display the canvas in the UI.
        # ? It's kind of disgusting and I hate it but I couldn't figure out how to do it in QSS. If we could figure that out, it'd be much better.
        image = QPixmap("images/sample_driver.jpg")
        image = image.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        canvas = QPixmap(100, 100)
        canvas.fill(Qt.GlobalColor.transparent)
        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter_path = QPainterPath()
        painter_path.addEllipse(0, 0, 100, 100)
        painter.setClipPath(painter_path)
        painter.drawPixmap(0, 0, image)
        painter.end()

        image_holder = QLabel()
        image_holder.setPixmap(canvas)
        image_holder.setFixedSize(100, 100)
        
        name = QLabel("NAME")
        horizontal_line = QFrame(frameShape=QFrame.Shape.HLine)
        about = QLabel("ABOUT")

        about_text = QLabel("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.")
        about_text.setWordWrap(True)
        about_text.setAlignment(Qt.AlignmentFlag.AlignJustify)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(about_text)

        basic_info.addWidget(image_holder, alignment=Qt.AlignmentFlag.AlignHCenter)
        basic_info.addWidget(name, alignment=Qt.AlignmentFlag.AlignHCenter)

        bio.addWidget(about, alignment=Qt.AlignmentFlag.AlignHCenter)
        bio.addWidget(scroll_area)

        basic_info.setContentsMargins(10, 10, 10, 10)
        bio.setContentsMargins(10, 10, 10, 10)

        layout.addLayout(basic_info)
        layout.addWidget(horizontal_line)
        layout.addLayout(bio)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addStretch()

# Right side, contains their placement history and their career stats
class DriverStatsSection(QWidget):
    def __init__(self, view_model: DriverProfilesViewModel):
        super().__init__()
        self.view_model = view_model

        # TODO: Replace with a name argument later
        driver_stats = self.view_model.get_career_stats("max-verstappen")

        # TODO: Pull this from Viewmodel later
        placement_history = [8, 1, 2, 1, 4]
        location_history = ["London", "Paris", "Norway", "Quatar", "Turkey"]

        layout = QVBoxLayout(self)
        placements = QVBoxLayout()
        race_history = QHBoxLayout()

        placements_text = QLabel("Placements")
        placements.addWidget(placements_text, alignment=Qt.AlignmentFlag.AlignCenter)

        formatted_cards = self.view_model.get_formatted_placements(placement_history, location_history)

        for placement_str, location_str in formatted_cards:
            card_frame = QFrame()
            card_frame.setFrameShape(QFrame.Shape.StyledPanel)
            card_frame.setFixedSize(70, 70)
            card_layout = QVBoxLayout(card_frame)
            placement_label = QLabel(placement_str)
            location_label = QLabel(location_str)
            card_layout.addWidget(placement_label, alignment=Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(location_label, alignment=Qt.AlignmentFlag.AlignCenter)
            race_history.addWidget(card_frame)

        race_history.addStretch()
        race_history.setContentsMargins(10, 10, 10, 10)
        race_widget = QWidget()
        race_widget.setLayout(race_history)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(race_widget)
        scroll_area.setFixedHeight(110)


        career_stats_layout = QGridLayout()
        career_stats_title = QLabel("Career Stats")

        career_stats_layout.addWidget(career_stats_title, 0, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)

        for row_idx, (title, stat) in enumerate(driver_stats.items(), start=1):
            self._populate_career_stats(career_stats_layout, row_idx, title, stat)

        career_stats_widget = QWidget()
        career_stats_widget.setLayout(career_stats_layout)

        career_stats_scroll = QScrollArea()
        career_stats_scroll.setWidgetResizable(True)
        career_stats_scroll.setWidget(career_stats_widget)

        placements.addWidget(scroll_area)
        layout.addLayout(placements)
        layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine))
        layout.addWidget(career_stats_scroll)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignRight)

    def _populate_career_stats(self, grid: QGridLayout, row: int, label: str, data: typing.Any) -> None:
        _label = QLabel(label)
        _data = QLabel(data)

        # ? Leaves space for the horizontal divider between each row
        grid_row = row * 2

        grid.addWidget(_label, grid_row, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(_data, grid_row, 1, alignment=Qt.AlignmentFlag.AlignRight)

        horizontal_line = QFrame(frameShape=QFrame.Shape.HLine)
        grid.addWidget(horizontal_line, grid_row + 1, 0, 1, 2)
                
