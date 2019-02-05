''' 
A module to provide C-like Enum behaviour

Taken from Recipe 16.9 of the Python Cookbook, 2nd ed., 
by Alex Martelli, Anna Martelli Ravenscroft and David Ascher 
(O'Reilly Media, 2005) 0596-00797-3
'''

class EnumException(Exception):
    pass

class Enumeration(object):
    def __init__(self, name, enumList, valuesAreUnique=True):
        self.__doc__ = name
        self.lookup = lookup = {}
        self.reverseLookup = reverseLookup = {}
        i = 0
        for x in enumList:
            if type(x) is tuple:
                try:
                    x, i = x
                except ValueError:
                    raise EnumException, "tuple doesn't have 2 items: %r" % (x,)
            if type(x) is not str:
                raise EnumException, "enum name is not a string: %r", x
            if type(i) is not int:
                raise EnumException, "enum value is not a string: %r", i
            if x in lookup:
                raise EnumException, "enum name is not unique: %r", x
            if valuesAreUnique and (i in reverseLookup):
                raise EnumException, "enum value %r not unique for %r", (i, x)
            lookup[x] = i
            reverseLookup[i] = x
            i += 1

    def __getattr__(self, attr):
        try: return self.lookup[attr]
        except KeyError: raise AttributeError, attr

    def whatis(self, value):
        return self.reverseLookup[value]
