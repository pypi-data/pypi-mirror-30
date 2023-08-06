# Interactive Components' imports
from interactive_components import config

"""
This module is used to manage CL custom output colors
"""

# Default CL color code
_clear = "\033[0m"


class Color:
    """
    Class used to define a custom CL output color by providing its color code.

    If the 'colored' value is setted to 'False' in the Interactive Components' general
    configuration, then the default CL color code is returned.
    """

    def __init__(self, code):
        self.code = code

    def __str__(self):
        return self.code if config.COLORED else _clear


# Pre-defined custom CL colors
CLEAR = Color(_clear)
RED = Color("\033[91m")
GREEN = Color("\033[92m")
YELLOW = Color("\033[93m")
DARK_BLUE = Color("\033[94m")
BLUE = Color("\033[96m")
WHITE = Color("\033[97m")
