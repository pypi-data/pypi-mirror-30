#!/usr/bin/python

"""!
@package 
TBD
Name(__init__.py)
Project_name(gsyslog)
User(PC)
Product_name(PyCharm)
@author <A href='email:fulkgl@gmail.com'>George L Fulk</A>
@version 0.10
"""

__author__ = "George L Fulk"
__version__ = 0.10

import sys


class MyClass(object):
    """!
    TBD MyClass
    """

    def __init__(self):
        """!
        Class constructor, create a new instance of this class.
        """
        pass

    def __str__(self):
        """!
        Override super class object definition for returning
        a string representation of this class instiatiation.
        Example usage:
        @code{.py}
            obj = MyClass()
            print(obj)
        @endcode
        @param self this object pointer reference
        @return String representing this class object
        """
        return "Me"


def main():
    return 0


if __name__ == "__main__":
    # command line entry point
    main()
