# Standard Library's imports
import re

# Interactive Components' imports
from interactive_components import color
from interactive_components import output_block
from interactive_components._type_checker_decorator import type_checker

"""
This module is used to build and print a static editor.
The editor is composed by various fields that the user can assign a value to.
Each field can be selected by introducing its corresponding index.
Once a field is selected, the user will be able to assign a value to it.
Edition finishes when the user selects the DONE option.


This module contains:
 - Field: Class defining each editor's field
 - Editor: Class defining the editor itself


* Example:

1. Field1: Value1
2. Field2: Value2
3. Field3: 
SELECT AN OPTION: 3
Field3 (Description for Field3): Value3
"""


@type_checker
class _FieldConfig:
    """
    Defines the menu field's configuration values

    UI Configuration:
        NUM_COLOR -> Color for the index number corresponding to the current field
        FIELD_COLOR -> Color for the current field's name
        VALUE_COLOR -> Color for the current field's value
        DESCRIPTION_COLOR -> Color for the current field's description

    UX Configuration:
        INVALID_VALUE_TEXT -> Defines the error text to show when the user's input value does not correspond to a
                              valid value for the current field
    """

    NUM_COLOR = color.Color
    FIELD_COLOR = color.Color
    VALUE_COLOR = color.Color
    DESCRIPTION_COLOR = color.Color
    INVALID_VALUE_TEXT = str

    def __init__(self):
        """ Sets the field's configuration default values """
        self.NUM_COLOR = color.WHITE
        self.FIELD_COLOR = color.WHITE
        self.VALUE_COLOR = color.GREEN
        self.DESCRIPTION_COLOR = color.BLUE
        self.INVALID_VALUE_TEXT = ""


@type_checker
class Field:
    """
    Class used to define a certain editor's field

    field -> String defining the field's name
    valid_regex -> String defining the field's valid values as a regular expression
    description -> String defining the field's description
    config -> Defines the configuration for this field

    * NOT TYPED
    value -> Defining the field's value
    """

    field = str
    valid_regex = str
    description = str
    config = _FieldConfig

    def __init__(self, field, valid_regex, default_value="", description=""):
        self.field = field
        self.valid_regex = valid_regex
        self.value = default_value
        self.description = "(" + description + ")" if description != "" else description
        self.config = _FieldConfig()


@type_checker
class _EditorConfig:
    """
    Defines the editor's configuration values

    UI Configuration:
       QUESTION_COLOR -> Color for editor's bottom question that asks the user to insert a field index
       INPUT_COLOR -> Color for the user's input
       DONE_NUM_COLOR -> Color for the editor's DONE option index
       DONE_TEXT_COLOR -> Color for the editor's DONE option text

    UX Configuration:
        QUESTION_TEXT -> Defines the text for the editor's bottom question that asks the user to insert a field index
        INVALID_OPTION_TEXT -> Defines the error text to show when the user's input does not correspond to a valid
                               editor's field index
       DONE_TEXT -> Defines the text for the editor's DONE option
    """

    QUESTION_COLOR = color.Color
    INPUT_COLOR = color.Color
    DONE_TEXT_COLOR = color.Color
    DONE_NUM_COLOR = color.Color
    QUESTION_TEXT = str
    INVALID_OPTION_TEXT = str
    DONE_TEXT = str

    def __init__(self):
        """ Sets the editor's configuration default values """
        self.QUESTION_COLOR = color.GREEN
        self.INPUT_COLOR = color.CLEAR
        self.DONE_NUM_COLOR = color.WHITE
        self.DONE_TEXT_COLOR = color.GREEN
        self.QUESTION_TEXT = "SELECT AN OPTION"
        self.INVALID_OPTION_TEXT = "The option selected is not available. Please, select a valid option from the menu above."
        self.DONE_TEXT = "DONE"


@type_checker
class Editor:
    """
    Class used to build and print a static editor.

    fields -> List of Field instances that the editor will contain
    config -> Defines the configuration for this editor
    _values -> List of values corresponding to each field
    """

    fields = list
    config = _EditorConfig
    _values = []

    def __init__(self, fields):
        self.fields = fields
        self.config = _EditorConfig()

        # For each field, defines its INVALID_VALUE_TEXT configuration value (If not already defined)
        for field in self.fields:
            if field.config.INVALID_VALUE_TEXT == "":
                field.config.INVALID_VALUE_TEXT = "Value must match regex '" + field.valid_regex + "'"

        # Defines a new OutputBlock instance
        self.output_block = output_block.OutputBlock()

    def build(self):
        """ Builds the editor """

        # Prints each menu Field prepended by its index
        i = 1
        for field in self.fields:
            self.output_block.printOutput(str(field.config.NUM_COLOR) +
                                          str(i) +
                                          ". " +
                                          str(field.config.FIELD_COLOR) +
                                          field.field +
                                          ": " +
                                          str(field.config.VALUE_COLOR) +
                                          field.value)
            i += 1

        # Prints the editor's DONE option
        self.output_block.printOutput(str(self.config.DONE_NUM_COLOR) +
                                      str(i) +
                                      ". " +
                                      str(self.config.DONE_TEXT_COLOR) +
                                      self.config.DONE_TEXT)

        # Asks the user to choose a field and returns the index for the selected one
        fieldId = self._getField()

        # Checks if the selected option corresponds to the DONE option or not
        if fieldId == len(self.fields) + 1:
            # If it is the DONE option
            # Fills the _values list with each field's value
            for field in self.fields:
                self._values.append(field.value)
        else:
            # If it is not the DONE option
            # Asks the user to assign a value to the selected field and assigns it to its Field instance
            self._editField(fieldId - 1)

        # Returns the _values list
        return self._values

    def _getField(self):
        """ Asks the user to choose a field and returns the index for the selected one """

        # Asks the user to select an field
        field = self.output_block.input(str(self.config.QUESTION_COLOR) +
                                        self.config.QUESTION_TEXT +
                                        ": " +
                                        str(self.config.INPUT_COLOR))

        # Checks if the introduced field index is valid or not
        if not field.isdigit() or not (0 < int(field) <= len(self.fields) + 1):
            # If it is not valid
            # Prints an error to alert the user that the selected index is invalid
            self.output_block.printError(self.config.INVALID_OPTION_TEXT)
            # Asks the user to select a field again
            return self._getField()
        else:
            # If it is valid
            # Resets the CL color to its default one
            print(str(color.CLEAR), end='')
            # Returns the selected field's index
            return int(field)

    def _editField(self, fieldId):
        """ Asks the user to assign a value to the selected field and assigns it to its Field instance """

        # Prints the selected field, its description, and asks the user to enter a value for it
        field = self.fields[fieldId]
        value = self.output_block.input(str(field.config.FIELD_COLOR) +
                                        field.field +
                                        " " +
                                        str(field.config.DESCRIPTION_COLOR) +
                                        field.description +
                                        str(field.config.FIELD_COLOR) +
                                        ": " +
                                        str(field.config.VALUE_COLOR))

        # Checks if the introduced value is valid or not for the selected field (matches the defined regex)
        if (re.match(field.valid_regex, value)):
            # If it is a valid value
            # Assigns it to its Field instance
            self.fields[fieldId].value = value
            # Rebuilds the editor
            self._rebuildEditor()
        else:
            # If it is not valid
            # Prints an error to alert the user that the introduced value is invalid
            self.output_block.printError(field.config.INVALID_VALUE_TEXT)
            # Asks the user to enter a value for the selected field again
            self._editField(fieldId)

    def _rebuildEditor(self):
        """ Rebuilds the editor """

        # Clears the OutputBlock containing the editor itseld
        self.output_block.clearOutput()
        # Rebuilds the editor
        self.build()
