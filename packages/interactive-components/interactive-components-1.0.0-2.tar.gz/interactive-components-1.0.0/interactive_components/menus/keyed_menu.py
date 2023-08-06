# Interactive Components' imports
from interactive_components import color
from interactive_components import utils
from interactive_components._type_checker_decorator import type_checker

"""
This module is used to build and print a keyed menu to be able to select one of several options.
An custom key wrapped inside [] will be assigned to each menu option.
The desired option can be selected by introducing the corresponding option key.

This module contains:
 - Option: Class defining each menu's option
 - Menu: Class defining the menu itself


* Example:

[A] Option1
[B] Option2
[C] Option3
SELECT AN OPTION:
"""


@type_checker
class _OptionConfig:
    """
    Defines the menu option's configuration values

    UI Configuration:
        KEY_COLOR -> Color for the key assigned to the current option
        OPTION_COLOR -> Color for the current option's text
    """

    KEY_COLOR = color.Color
    OPTION_COLOR = color.Color

    def __init__(self):
        """ Sets the option's configuration default values """
        self.KEY_COLOR = color.WHITE
        self.OPTION_COLOR = color.WHITE


@type_checker
class Option:
    """
    Class used to define a certain menu's option

    option -> String that defines the option itself
    key -> String that defines the option's key
    config -> Defines the configuration for this option
    """

    option = str
    key = str
    config = _OptionConfig

    def __init__(self, option, key):
        self.option = option
        self.key = key
        self.config = _OptionConfig()


@type_checker
class _MenuConfig:
    """
    Defines the menu's configuration values

    UI Configuration:
        QUESTION_COLOR -> Color for menu's bottom question that asks the user to insert an option key
        INPUT_COLOR -> Color for the user's input

    UX Configuration:
        QUESTION_TEXT -> Defines the text for the menu's bottom question that asks the user to insert an option key
        INVALID_OPTION_TEXT -> Defines the error text to show when the user's input does not correspond to a valid
                               menu's option key
        CASE_SENSITIVE -> Boolean that defines if the key selection is case sensitive or not
    """

    QUESTION_COLOR = color.Color
    INPUT_COLOR = color.Color
    QUESTION_TEXT = str
    INVALID_OPTION_TEXT = str
    CASE_SENSITIVE = bool

    def __init__(self):
        """ Sets the menu's configuration default values """
        self.QUESTION_COLOR = color.GREEN
        self.INPUT_COLOR = color.CLEAR
        self.QUESTION_TEXT = "SELECT AN OPTION"
        self.INVALID_OPTION_TEXT = "The option selected is not available. Please, select a valid option from the menu above."
        self.CASE_SENSITIVE = False


@type_checker
class Menu:
    """
    Class used to build and print a keyed menu to be able to select one of several options.

    options -> List of Option instances that the menu will contain
    config -> Defines the configuration for this menu
    keys -> List of keys assigned to each menu option
    """

    options = list
    config = _MenuConfig
    keys = []

    def __init__(self, options):
        self.options = options
        self.config = _MenuConfig()

        # Fills the keys list with each Option key
        for option in options:
            self.keys.append(option.key)

        # Checks if there are any KEY assigned twice and throws an error if that is the case
        if len(self.keys) != len(set(self.keys)):
            raise ValueError("Two menu options can not have the same KEY value")

    def build(self):
        """ Builds the menu """

        # Prints each menu Option prepended by its own key
        for option in self.options:
            print(str(option.config.KEY_COLOR) +
                  "[" +
                  option.key +
                  "] " +
                  str(option.config.OPTION_COLOR) +
                  option.option)

        # Asks the user to choose an option in the menu and returns the selected one
        return self._getOption()

    def _getOption(self):
        """ Asks the user to choose an option in the menu and returns the selected one """

        # Asks the user to select an option
        option = input(str(self.config.QUESTION_COLOR) +
                       self.config.QUESTION_TEXT +
                       ": " +
                       str(self.config.INPUT_COLOR))

        # Checks if the introduced option key is valid or not
        if (self.config.CASE_SENSITIVE and option in self.keys) or (
                    not self.config.CASE_SENSITIVE and option.lower() in map(lambda key: key.lower(), self.keys)):
            # If it is a valid option
            # Resets the CL color to its default one
            print(str(color.CLEAR), end='')
            # Returns the selected menu's option index
            return option
        else:
            # If it is not valid
            # Prints an error to alert the user that the selected key is invalid
            utils.printError(self.config.INVALID_OPTION_TEXT)
            # Asks the user to select a menu option again
            return self._getOption()
