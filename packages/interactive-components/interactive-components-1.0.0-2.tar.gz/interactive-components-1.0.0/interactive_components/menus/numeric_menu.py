# Interactive Components' imports
from interactive_components import color
from interactive_components import utils
from interactive_components._type_checker_decorator import type_checker

"""
This module is used to build and print a numeric menu to be able to select one of several options.
An index will be assigned to each menu option.
The desired option can be selected by introducing the corresponding option index.

This module contains:
 - Option: Class defining each menu's option
 - Menu: Class defining the menu itself


* Example:

1. Option1
2. Option2
3. Option3
SELECT AN OPTION:
"""


@type_checker
class _OptionConfig:
    """
    Defines the menu option's configuration values

    UI Configuration:
        NUM_COLOR -> Color for the index number corresponding to the current option
        OPTION_COLOR -> Color for the current option's text
    """

    NUM_COLOR = color.Color
    OPTION_COLOR = color.Color

    def __init__(self):
        """ Sets the option's configuration default values """
        self.NUM_COLOR = color.WHITE
        self.OPTION_COLOR = color.WHITE


@type_checker
class Option:
    """
    Class used to define a certain menu's option

    option -> String that defines the option itself
    config -> Defines the configuration for this option
    """

    option = str
    config = _OptionConfig

    def __init__(self, option):
        self.option = option
        self.config = _OptionConfig()


@type_checker
class _MenuConfig:
    """
    Defines the menu's configuration values

    UI Configuration:
        QUESTION_COLOR -> Color for menu's bottom question that asks the user to insert an option index
        INPUT_COLOR -> Color for the user's input

    UX Configuration:
        QUESTION_TEXT -> Defines the text for the menu's bottom question that asks the user to insert an option index
        INVALID_OPTION_TEXT -> Defines the error text to show when the user's input does not correspond to a valid
                               menu's option index
    """

    QUESTION_COLOR = color.Color
    INPUT_COLOR = color.Color
    QUESTION_TEXT = str
    INVALID_OPTION_TEXT = str

    def __init__(self):
        """ Sets the menu's configuration default values """
        self.QUESTION_COLOR = color.GREEN
        self.INPUT_COLOR = color.CLEAR
        self.QUESTION_TEXT = "SELECT AN OPTION"
        self.INVALID_OPTION_TEXT = "The option selected is not available. " +\
                                   "Please, select a valid option from the menu above."


@type_checker
class Menu:
    """
    Class used to build and print a numeric menu to be able to select one of several options.

    options -> List of Option instances that the menu will contain
    config -> Defines the configuration for this menu
    """

    options = list
    config = _MenuConfig

    def __init__(self, options):
        self.options = options
        self.config = _MenuConfig()

    def build(self):
        """ Builds the menu """

        # Prints each menu Option prepended by its index
        option_index = 1
        for option in self.options:
            print(str(option.config.NUM_COLOR) +
                  str(option_index) + ". " +
                  str(option.config.OPTION_COLOR) +
                  option.option)
            option_index += 1

        # Asks the user to choose an option in the menu and returns the selected one
        return self._getOption()

    def _getOption(self):
        """ Asks the user to choose an option in the menu and returns the selected one """

        # Asks the user to select an option
        option = input(str(self.config.QUESTION_COLOR) +
                       self.config.QUESTION_TEXT +
                       ": " +
                       str(self.config.INPUT_COLOR))

        # Checks if the introduced option index is valid or not
        if not option.isdigit() or not (0 < int(option) <= len(self.options)):
            # If it is not valid
            # Prints an error to alert the user that the selected index is invalid
            utils.printError(self.config.INVALID_OPTION_TEXT)
            # Asks the user to select a menu option again
            return self._getOption()

        else:
            # If it is a valid option
            # Resets the CL color to its default one
            print(str(color.CLEAR), end='')
            # Returns the selected menu's option index
            return int(option)
