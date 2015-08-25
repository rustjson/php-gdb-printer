"""GDB Pretty printers and conveience functions for PHP internel debuging

Author: Jason Young <red.wolf.s.husband@gmail.com>


"""

from __future__ import print_function
import re
import sys 
#import gdb.printing

print("Loading PHP Internal Debug Printer...DONE?", file=sys.stderr)

#phpobjfile = gdb.current_objfile() or gdb.objfiles()[0]

#phpobjfile.pretty_printers = []


class PHPZvalPrinter():
    "Print a zval"
    
    def __init__(self, val):
        self.val = val;

    def to_string(self):
        if (self.val['u1']['type_info'] == 6): 
            zend_str = self.val['value']['str']

            _str = zend_str['val'].string('iso8859-1', 'ignore', int(zend_str['len']));
            return "[IS_STRING] " +  _str
        else:
            return 'NULL'

    def display_hint(self):
        return 'zval'

def zval_lookup_function (val):
    if str(val.type) == "zval *":
        return PHPZvalPrinter(val)
    return None

gdb.pretty_printers.append(zval_lookup_function)
