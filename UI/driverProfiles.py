from PySide6.QtWidgets import (
    QLabel,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFrame,
    QSizePolicy,
    QScrollArea,
    QGridLayout,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from ViewModels.driverProfilesVM import DriverProfilesViewModel
import typing

"""
@brief page for the driver profiles
"""


class DriverProfiles(QWidget):
    def __init__(self, view_model: DriverProfilesViewModel):
        super().__init__()
        self.view_model = view_model
        self.driver_codes = self.view_model.get_driver_codes()

        grid = QGridLayout(self)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(0)

        self.nav_bar = DriverNavBar(self.driver_codes)

        self.nav_bar.driver_selected.connect(self.view_model.select_driver)

        grid.addWidget(self.nav_bar, 0, 0, 1, 2)

        self.driver_about_section = DriverAboutSection(self.view_model)

        self.view_model.bio_loaded.connect(self.driver_about_section.update_bio)
        self.view_model.name_loaded.connect(self.driver_about_section.update_name)
        self.view_model.img_loaded.connect(self.driver_about_section.update_img)

        grid.addWidget(self.driver_about_section, 1, 0)

        # TODO: We lost a vertical line here :(

        self.driver_stats_section = DriverStatsSection(self.view_model)
        grid.addWidget(self.driver_stats_section, 1, 1)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)


# Top nav bar. This should probably be a search bar in hindsight, but I like the design of this right now so we're going with it.
class DriverNavBar(QWidget):
    driver_selected = Signal(str)

    def __init__(self, driver_codes: list[str]):
        super().__init__()

        drivers = driver_codes

        layout = QVBoxLayout(self)
        driver_container = QHBoxLayout()

        driver_labels = QLabel("Drivers")
        vertical_line = QFrame(frameShape=QFrame.Shape.VLine)
        horizontal_line = QFrame(frameShape=QFrame.Shape.HLine)

        vertical_line.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        driver_container.addWidget(driver_labels)
        driver_container.addWidget(vertical_line)

        for driver in drivers:
            driver_button = QPushButton(driver)

            driver_button.clicked.connect(
                lambda checked=False, code=driver: self._on_driver_button_clicked(code)
            )

            driver_container.addWidget(driver_button)

        driver_container.setContentsMargins(0, 0, 0, 0)
        driver_container.setSpacing(10)

        driver_container_widget = QWidget()
        driver_container_widget.setLayout(driver_container)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(driver_container_widget)

        layout.addWidget(scroll_area)
        layout.addWidget(horizontal_line)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def _on_driver_button_clicked(self, code):
        self.driver_selected.emit(code)


# Left side, contains a picture, the name of the driver, and their biography
class DriverAboutSection(QWidget):
    driver_bio = Signal(str)
    driver_name = Signal(str)
    driver_img = Signal(str)

    def __init__(self, view_model: DriverProfilesViewModel):
        super().__init__()
        self.view_model = view_model

        layout = QVBoxLayout(self)
        basic_info = QVBoxLayout()
        bio = QVBoxLayout()

        self.image_holder = QLabel()
        self.image_holder.setPixmap(QPixmap("images/sample_driver.jpg"))
        self.image_holder.setFixedSize(100, 100)

        self.name = QLabel("NAME")
        horizontal_line = QFrame(frameShape=QFrame.Shape.HLine)
        about = QLabel("ABOUT")

        self.about_text = QLabel("Click on a driver to view their biography.")
        self.about_text.setWordWrap(True)
        self.about_text.setAlignment(Qt.AlignmentFlag.AlignJustify)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.about_text)

        basic_info.addWidget(self.image_holder, alignment=Qt.AlignmentFlag.AlignHCenter)
        basic_info.addWidget(self.name, alignment=Qt.AlignmentFlag.AlignHCenter)

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

    def update_bio(self, bio_text: str) -> None:
        self.about_text.setText(bio_text)

    def update_name(self, driver_name: str) -> None:
        self.name.setText(driver_name)

    def update_img(self, pixmap: QPixmap) -> None:
        self.image_holder.setPixmap(pixmap)


# Right side, contains their placement history and their career stats
class DriverStatsSection(QWidget):
    def __init__(self, view_model: DriverProfilesViewModel):
        super().__init__()
        self.view_model = view_model

        # TODO: Pull this from Viewmodel later
        placement_history = [8, 1, 2, 1, 4]
        location_history = ["London", "Paris", "Norway", "Quatar", "Turkey"]

        layout = QVBoxLayout(self)
        placements = QVBoxLayout()
        race_history = QHBoxLayout()

        placements_text = QLabel("Placements")
        placements.addWidget(placements_text, alignment=Qt.AlignmentFlag.AlignCenter)

        formatted_cards = self.view_model.get_formatted_placements(
            placement_history, location_history
        )

        for placement_str, location_str in formatted_cards:
            card_frame = QFrame()
            card_frame.setFrameShape(QFrame.Shape.StyledPanel)
            card_frame.setFixedSize(70, 70)
            card_layout = QVBoxLayout(card_frame)
            placement_label = QLabel(placement_str)
            location_label = QLabel(location_str)
            card_layout.addWidget(
                placement_label, alignment=Qt.AlignmentFlag.AlignCenter
            )
            card_layout.addWidget(
                location_label, alignment=Qt.AlignmentFlag.AlignCenter
            )
            race_history.addWidget(card_frame)

        race_history.addStretch()
        race_history.setContentsMargins(10, 10, 10, 10)
        race_widget = QWidget()
        race_widget.setLayout(race_history)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(race_widget)
        scroll_area.setFixedHeight(110)

        self.career_stats_layout = QGridLayout()
        self.career_placeholder = QLabel("No Stats. Select a driver to see stats!")
        self.career_stats_layout.addWidget(self.career_placeholder)

        career_stats_widget = QWidget()
        career_stats_widget.setLayout(self.career_stats_layout)

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

        self.view_model.stats_loaded.connect(self.update_stats)

    def update_stats(self, driver_stats: dict[str, str]) -> None:
        while self.career_stats_layout.count():
            item = self.career_stats_layout.takeAt(0)

            # ? PyLance was being an ass about "None" not having .deleteLater() despite a very elegant assert statement (assert item is not None)
            # ?     so now we have to deal with this and it's ugly and I hate it with all my heart <3
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        career_stats_title = QLabel("Career Stats")

        self.career_stats_layout.addWidget(
            career_stats_title, 0, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter
        )

        for row_idx, (title, stats) in enumerate(driver_stats.items(), start=1):
            self._populate_career_stats(self.career_stats_layout, row_idx, title, stats)

    def _populate_career_stats(
        self, grid: QGridLayout, row: int, label: str, data: typing.Any
    ) -> None:
        _label = QLabel(label)
        _data = QLabel(data)

        # ? Leaves space for the horizontal divider between each row
        grid_row = row * 2

        grid.addWidget(_label, grid_row, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(_data, grid_row, 1, alignment=Qt.AlignmentFlag.AlignRight)

        horizontal_line = QFrame(frameShape=QFrame.Shape.HLine)
        grid.addWidget(horizontal_line, grid_row + 1, 0, 1, 2)
