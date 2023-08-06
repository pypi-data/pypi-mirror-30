# Standard Library's imports
import os

# Interactive Components' imports
from interactive_components import color
from interactive_components import config

"""
This module contains some useful general utilities that can be used when building
interactive python scripts, such as printing errors, warnings or cleaning the
entire command line.
"""


def printError(error_message):
    """Prints a RED error message in the console"""
    printColored(config.ERROR_KEY + ": " + error_message, color.RED)


def printWarning(warning_message):
    """Prints a YELLOW warning message in the console"""
    printColored(config.WARNING_KEY + ": " + warning_message, color.YELLOW)


def printColored(message, output_color):
    """Prints a colored output message in the console"""
    print(str(output_color) + message + str(color.CLEAR))


def clear():
    """Clears the whole command line content"""
    os.system('clear')
