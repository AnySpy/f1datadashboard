from dataclasses import dataclass

@dataclass
class DayTheme:
    # UI colors
    background: str = "#16161f"
    primaryText: str = "#ffffff"
    secondaryText: str = "#a0a0b0"
    tertiaryText: str = "#000000"
    # information colors
    success: str = "#00ff59"
    warning: str = "#fff200"
    danger: str = "#e33d3d"
    info: str = "#3e85d1"

theme = DayTheme()