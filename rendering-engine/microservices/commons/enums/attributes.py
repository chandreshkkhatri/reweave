"""
Common enums being used in the project
"""

from enum import Enum

class Position(str,Enum):
    """Position"""
    CENTER = 'center'

class TextClipMethod(str,Enum):
    """Text Clip Method"""
    CAPTION = 'caption',
    LABEL = 'label'

class Fonts(str,Enum):
    """Font Families"""
    AMIRI_REGULAR = 'Amiri-regular'
    CALIBRI = 'Calibri'
    Nirmala_UI = 'Nirmala-UI'
    VERDANA = 'Verdana'

class Colors(str,Enum):
    """Colors"""
    WHITE = 'white'
    ORANGE = 'orange'
    GREEN = 'green'
    BLACK = 'black'