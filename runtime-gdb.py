"""GDB Pretty printers and conveience functions for PHP internel debuging

Author: Jason Young <red.wolf.s.husband@gmail.com>


"""

from __future__ import print_function
import re
import sys 

print("Loading PHP Internal Debug Printer...DONE?", file=sys.stderr)



class PHPZvalPrinter():
    "Print a zval"
    
    def __init__(self, val):
        self.val = val;

    def to_string(self):
        ztype = self.val['u1']['v']['type'];

        if (ztype == 4):
            return "(IS_LONG) " + str(self.val['value']['lval'])
        
        elif (ztype == 5):
            return "(IS_DOUBLE) " + str(self.val['value']['dval'])

        elif (ztype == 6): 
            zend_str = self.val['value']['str']
            return PHPZendStringPrinter(zend_str).to_string();
        
        elif (ztype == 7): 
            return PHPHashTablePrinter(self.val['value']['arr']).to_string();
        
        elif (ztype == 10):#zend_reference
            zend_reference = self.val['value']['ref']
            return "(IS_REFERENCE) {refcount=" + str(zend_reference['gc']['refcount']) + ", val={" + PHPZvalPrinter(zend_reference['val']).to_string()  + "}}";

        else:
            return 'NULL'

    def display_hint(self):
        return 'zval *'

class PHPZendStringPrinter():
    "print a zend string"

    def __init__(self, val):
        self.val = val;
    
    #Still need to work on this. cause len is not actual string len
    def to_string(self):
        len = int(self.val['len'])

        if len > 100:
            len = 100
            etc = "..."
       
        _str = self.val['val'].string('iso8859-1', 'ignore', len);
        return "(IS_STRING) [" + _str + "...]"
    
    def display_hint(self):
        return 'zend_string *'

class PHPHashTablePrinter():
    "print a zend hash table"

    def __init__(self, val):
        self.val = val;

    def to_string(self):
        nNumOfElements = self.val['nNumOfElements'];
        nTableSize = self.val['nTableSize'];
        nNumUsed = self.val['nNumUsed'];

        _str = "{nNumUsed = " + str(nNumUsed) + ", nNumOfElements = " + str(nNumOfElements) + ", nTableSize = "+ str(nTableSize) +"}\n";

        pNum = 0;
        #only display 4 elements 
        if (nNumOfElements >= 4):
            pNum = 4;
        else:
            pNum = nNumOfElements;

        for i in xrange(pNum):
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
