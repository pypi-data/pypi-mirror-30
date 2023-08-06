# Standard Library's imports
import re

# Interactive Components' imports
from interactive_components import color
from interactive_components import utils
from interactive_components._type_checker_decorator import type_checker

"""
This module is used to build and print a sequential editor.
The editor is composed by various fields that the user can assign a value to.
Each field will be sequentially presented one after the other.
The user can assign a value to a field once it is presented.
When the user assigns a value to a field, the next field will be presented.

This module contains:
 - Field: Class defining each editor's field
 - Editor: Class defining the editor itself


* Example:

Field1 (Description for Field1): Value1
Field2 (Description for Field2):
"""


@type_checker
class _FieldConfig:
    """
    Defines the menu field's configuration values

    UX Configuration:
        INVALID_VALUE_TEXT -> Defines the error text to show when the user's input value does not correspond to a
                              valid value for the current field
    """

    INVALID_VALUE_TEXT = str

    def __init__(self):
        """ Sets the field's configuration default values """
        self.INVALID_VALUE_TEXT = ""


@type_checker
class Field:
    """
    Class used to define a certain editor's field

    field -> String defining the field's name
    valid_regex -> String defining the field's valid values as a regular expression
    description -> String defining the field's description
    config -> Defines the configuration for this field
    """

    field = str
    valid_regex = str
    description = str
    config = _FieldConfig

    def __init__(self, field, valid_regex, description=""):
        self.field = field
        self.valid_regex = valid_regex
        self.description = "(" + description + ")" if description != "" else description
        self.config = _FieldConfig()


@type_checker
class _EditorConfig:
    """
    Defines the editor's configuration values

    UI Configuration:
       FIELD_COLOR -> Color for the field's name
       DESCRIPTION_COLOR -> Color for the field's description
       INPUT_COLOR -> Color for the user's input
    """

    FIELD_COLOR = color.Color
    DESCRIPTION_COLOR = color.Color
    INPUT_COLOR = color.Color

    def __init__(self):
        """ Sets the editor's configuration default values """
        self.FIELD_COLOR = color.GREEN
        self.DESCRIPTION_COLOR = color.BLUE
        self.INPUT_COLOR = color.WHITE


@type_checker
class Editor:
    """
    Class used to build and print a sequential editor.

    fields -> List of Field instances that the editor will contain
    config -> Defines the configuration for this editor
    """

    fields = list
    config = _EditorConfig

    def __init__(self, fields):
        self.fields = fields
        self.config = _EditorConfig()

        for field in self.fields:
            if field.config.INVALID_VALUE_TEXT == "":
                field.config.INVALID_VALUE_TEXT = "Value must match regex '" + field.valid_regex + "'"

    def build(self):
        """ Builds the editor """

        # For each field, asks the user to enter its value
        values = []
        for field in self.fields:
            values.append(self._getField(field))

        # Resets the CL color to its default one
        print(str(color.CLEAR), end='')

        # Returns the list of values assigned to each field
        return values

    def _getField(self, field):
        """ Asks the user to enter a value for the current field """

        # Asks the user to enter the value
        value = input(str(self.config.FIELD_COLOR) +
                      field.field +
                      " " +
                      str(self.config.DESCRIPTION_COLOR) +
                      field.description +
                      str(self.config.FIELD_COLOR) +
                      ": " + str(self.config.INPUT_COLOR))

        # Checks if the introduced value is valid or not for the current field (matches the defined regex)
        if (re.match(field.valid_regex, value)):
            # If it is a valid value, return it
            return value
        else:
            # If it is not valid
            # Prints an error to alert the user that the introduced value is invalid
            utils.printError(field.config.INVALID_VALUE_TEXT)
            # Asks the user to enter a value for the current field again
            return self._getField(field)
