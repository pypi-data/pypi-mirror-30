# Standard Library's imports
import sys

# Interactive Components' imports
from interactive_components import utils


class OutputBlock:
    """
    This class is used to be able to manage an output block. This means, to be able to wrap the
    output to the command line inside a block and keeping track of how many lines have been printed
    in total. This way, it can then be used to clear from the command line all this entire block of
    lines while keeping the rest of printed lines outside the block intact.

    In order to do so, instead of using the standard 'print' methods (or the ones provided by Interactive
    Components' utils), the 'print' methods of this manager class must be used.
    """

    def __init__(self):
        self.num_of_lines = 0

    def printOutput(self, str):
        """ Prints 'str' to the command line and updates the number of lines that have been printed """
        self.num_of_lines += 1 + str.count("\n")
        print(str)

    def printError(self, str):
        """ Prints a RED error to the command line and updates the number of lines that have been printed """
        self.num_of_lines += 1 + str.count("\n")
        utils.printError(str)

    def printWarning(self, str):
        """ Prints a YELLOW warning to the command line and updates the number of lines that have been printed """
        self.num_of_lines += 1 + str.count("\n")
        utils.printWarning(str)

    def input(self, str):
        """ Waits for a user input and updates the number of lines that have been printed """
        self.num_of_lines += 1 + str.count("\n")
        return input(str)

    def clearOutput(self):
        """ Clears all (and just) the lines that have been printed inside this block """
        for i in range(self.num_of_lines):
            sys.stdout.write("\033[F")
            sys.stdout.write("\033[K")
        self.num_of_lines = 0
