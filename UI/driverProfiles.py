from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QSizePolicy, QScrollArea
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QPainterPath
import typing
from Services.dbhandler import DBhandler

"""
@brief page for the driver profiles
"""

class DriverProfiles(QWidget):
    def __init__(self, dbHandler: DBhandler):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        information_layout = QHBoxLayout()
        information_layout.setContentsMargins(0, 0, 0, 0)
        information_layout.setSpacing(0)

        self.nav_bar = DriverNavBar()
        layout.addWidget(self.nav_bar)

        self.driver_about_section = DriverAboutSection()
        self.driver_about_section.setContentsMargins(0, 0, 0, 0)
        information_layout.addWidget(self.driver_about_section)

        self.vertical_line = QFrame(frameShape=QFrame.Shape.VLine)
        self.vertical_line.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.vertical_line.setContentsMargins(0, 0, 0, 0)
        information_layout.addWidget(self.vertical_line)

        self.driver_stats_section = DriverStatsSection()
        self.driver_stats_section.setContentsMargins(0, 0, 0, 0)
        information_layout.addWidget(self.driver_stats_section)

        layout.addLayout(information_layout)

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
        layout.addStretch()

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
    def __init__(self):
        super().__init__()

        # TODO: Pull this from DB
        placement_history = [8, 1, 2, 1, 4]
        location_history = ["London", "Paris", "Norway", "Quatar", "Turkey"]
        stats = ["38", "442", "1 (x8)", "15", "1 (x6)", "6", "0", "5"]

        layout = QVBoxLayout(self)
        placements = QVBoxLayout()
        race_history = QHBoxLayout()
        career_stats = QVBoxLayout()

        placements_text = QLabel("Placements")
        placements.addWidget(placements_text, alignment=Qt.AlignmentFlag.AlignCenter)
        
        for i in range(len(placement_history)):        
            card_frame = QFrame()
            card_frame.setFrameShape(QFrame.Shape.StyledPanel)
            card_frame.setFixedSize(70, 70)
            card_layout = QVBoxLayout(card_frame)
            placement_label = QLabel(self._placement_naming(placement_history[i]))
            location_label = QLabel(location_history[i])
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

        horizontal_line = QFrame(frameShape=QFrame.Shape.HLine)

        career_stats_title = QLabel("Career Stats")
        career_stats.addWidget(career_stats_title, alignment=Qt.AlignmentFlag.AlignCenter)

        self._populate_career_stats(career_stats, "Grand Prix Entered", stats[0])
        self._populate_career_stats(career_stats, "Career Points", stats[1])
        self._populate_career_stats(career_stats, "Highest Race Finish", stats[2])
        self._populate_career_stats(career_stats, "Podiums", stats[3])
        self._populate_career_stats(career_stats, "Highest Grid Position", stats[4])
        self._populate_career_stats(career_stats, "Pole Position", stats[5])
        self._populate_career_stats(career_stats, "World Championships", stats[6])
        self._populate_career_stats(career_stats, "DNFs", stats[7])

        career_stats_widget = QWidget()
        career_stats_widget.setLayout(career_stats)
        career_stats_scroll = QScrollArea()
        career_stats_scroll.setWidgetResizable(True)
        career_stats_scroll.setWidget(career_stats_widget)

        scroll_area.setFixedHeight(110)
        career_stats.setContentsMargins(10, 10, 10, 10)

        placements.addWidget(scroll_area)
        layout.addLayout(placements)
        layout.addWidget(horizontal_line)
        layout.addWidget(career_stats_scroll)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addStretch()

    def _populate_career_stats(self, parent_container: QVBoxLayout, label: str, data: typing.Any) -> None:
        container = QHBoxLayout()
        _label = QLabel(label)
        _data = QLabel(data)
        container.addWidget(_label, alignment=Qt.AlignmentFlag.AlignLeft)
        container.addWidget(_data, alignment=Qt.AlignmentFlag.AlignRight)
        parent_container.addLayout(container)
        parent_container.addWidget(QFrame(frameShape=QFrame.Shape.HLine))

    def _placement_naming(self, place: int) -> str:
        placement_string = ""

        match place:
            case 1:
                placement_string = "1st"
            case 2:
                placement_string = "2nd"
            case 3:
                placement_string = "3rd"
            case _:
                placement_string = f"{place}th"

        return placement_string

                
