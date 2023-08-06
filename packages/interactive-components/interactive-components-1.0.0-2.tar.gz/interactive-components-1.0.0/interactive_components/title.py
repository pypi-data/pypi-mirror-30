# Interactive Components' imports
from interactive_components import color
from interactive_components._type_checker_decorator import type_checker

"""
This module is used to build and print a title wrapped
in a box


* Example:
---------------
|    TITLE    |  
---------------   
"""


@type_checker
class _TitleConfig:
    """
    Defines the title's configuration values

    UI Configuration:
        BOX_COLOR -> Color for the title's wrapping box
        TITLE_COLOR -> Color for the title text
    """

    BOX_COLOR = color.Color
    TITLE_COLOR = color.Color

    def __init__(self):
        """ Sets the title's configuration default values """
        self.BOX_COLOR = color.BLUE
        self.TITLE_COLOR = color.BLUE


@type_checker
class Title:
    """
    Class used to build and print a title wrapped in a box

    title -> String that defines the title text
    config -> Defines the configuration for this title
    """

    title = str
    config = _TitleConfig

    def __init__(self, title):
        self.title = title
        self.config = _TitleConfig()

    def build(self):
        """ Builds the title inside the wrapping box """

        # Defines the upper and lower box lines with a length equal to the title's length plus a 4 spaces padding
        title_box = ""
        for _ in range(len(self.title) + 10): title_box += "-"

        # Prints the upper box line
        print(str(self.config.BOX_COLOR) +
              title_box)

        # Prints the title text in between of the two box side lines
        print("|    " +
              str(self.config.TITLE_COLOR) +
              self.title +
              str(self.config.BOX_COLOR) +
              "    |")

        # Prints the lower box line
        print(title_box +
              str(color.CLEAR))
