"""
A custom decorator used by classes to make them able to force a type to their attributes.
The attribute type must be defined at the class definition.


* Example: Class that contains a forced 'String' attribute

@type_checker
class ClassWithStringAttr:

    my_attr = str

    __init__(self, the_attr):
        self.my_attr = the_attr

If 'the_attr' is not a String, an exception will be thrown.
"""


def getter_setter_gen(attr_name, attr_type):
    """
    Defines the new 'getter' and 'setter' for the attribute.
    Checks if the new value's type matches the defined attribute's type at the 'setter'.
    """

    def getter(self):
        return getattr(self, "__" + attr_name)

    def setter(self, value):
        if not isinstance(value, attr_type):
            raise TypeError(
                "'" + str(attr_name) + "' attribute must be set to an instance of '" + str(attr_type.__name__) + "'")
        setattr(self, "__" + attr_name, value)

    return property(getter, setter)


def type_checker(class_):
    """
    Creates a new class, defining a 'setter' method for each class' attribute
    that checks if the value's type corresponds to the defined attribute's type.
    """

    attr_dict = {}

    for attr_name, attr_type in class_.__dict__.items():
        if isinstance(attr_type, type):
            attr_type = getter_setter_gen(attr_name, attr_type)
        attr_dict[attr_name] = attr_type

    return type(class_)(class_.__name__, class_.__bases__, attr_dict)
