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
        if (self.val['u1']['v']['type'] == 4):
            return "[IS_LONG] " + str(self.val['value']['lval'])
        
        elif (self.val['u1']['v']['type'] == 5):
            return "[IS_DOUBLE] " + str(self.val['value']['dval'])

        elif (self.val['u1']['v']['type'] == 6): 
            zend_str = self.val['value']['str']
            return PHPZendStringPrinter(zend_str).to_string();
        
        elif (self.val['u1']['v']['type'] == 7): 
            return PHPHashTablePrinter(self.val['value']['arr']).to_string();
        
        else:
            return 'NULL'

    def display_hint(self):
        return 'zval *'

class PHPZendStringPrinter():
    "print a zend string"

    def __init__(self, val):
        self.val = val;

    def to_string(self):
        _str = self.val['val'].string('iso8859-1', 'ignore', int(self.val['len']));
        return "(IS_STRING) [" + _str + "]"
    
    def display_hint(self):
        return 'zend_string *'

class PHPHashTablePrinter():
    "print a zend hash table"

    def __init__(self, val):
        self.val = val;

    def to_string(self):
        nNumOfElements = self.val['nNumOfElements'];
        nTableSize = self.val['nTableSize'];
        _str = "{nNumUsed = " + str(self.val['nNumUsed']) + ", nNumOfElements = " + str(nNumOfElements) + ", nTableSize = "+ str(nTableSize) +"}\n";

        for i in xrange(nNumOfElements):
            try:
                key = self.val['arData'][i]['key']
                val = self.val['arData'][i]['val']
                _str += PHPZendStringPrinter(key).to_string() + " => "
                _str += PHPZvalPrinter(val).to_string() + "\n"
            except:
                continue
        
        return "(HashTable) " +  _str
    
    def display_hint(self):
        return 'zend_string *'
        

def zval_lookup_function (val):
    if str(val.type) == "zval *":
        return PHPZvalPrinter(val)
    if str(val.type) == "zend_string *":
        return PHPZendStringPrinter(val)
    if str(val.type) == "HashTable *":
        return PHPHashTablePrinter(val)
    return None

gdb.pretty_printers.append(zval_lookup_function)
