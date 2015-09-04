"""GDB Pretty printers and conveience functions for PHP internel debuging

Author: Jason Young <red.wolf.s.husband@gmail.com>


"""

from __future__ import print_function
import re
import sys 
import traceback

print("Loading PHP Internal Debug Printer...DONE?", file=sys.stderr)



class PHPZvalPrinter():
    "Print a zval"
    
    def __init__(self, val):
        self.val = val;

    def to_string(self):
        ztype = self.val['u1']['v']['type'];

        if (ztype == 2):
            return "(FALSE) "
        if (ztype == 3):
            return "(TRUE) "
        if (ztype == 4):
            return "(LONG) " + str(self.val['value']['lval'])
        
        elif (ztype == 5):
            return "(DOUBLE) " + str(self.val['value']['dval'])

        elif (ztype == 6): 
            zend_str = self.val['value']['str']
            return "(ZVAL) {" + PHPZendStringPrinter(zend_str).to_string() + "}";
        
        elif (ztype == 7): 
            return "(ZVAL) {" + PHPHashTablePrinter(self.val['value']['arr']).to_string() + "}";
        
        #elif (ztype == 8):#zend_object 
        #    return "(ZVAL) {" + PHPZendObjectPrinter(self.val['value']['obj']).to_string() + "}";

        #elif (ztype == 10):#zend_reference
            #zend_reference = self.val['value']['ref']
            #return "(ZVAL) {" + PHPZendReferencePrinter(zend_reference).to_string() + "}";
        else:
            return 'No pretty printer[type=' + str(ztype) + ']';

    def display_hint(self):
        return 'zval *'

class PHPZendObjectPrinter():
    "print zend OBJECT"

    def __init__(self, val):
        self.val = val;
    
    def to_string(self):

        _str = "";
        _str += "(OBJECT) {gc=" + str(self.val['gc']['refcount']);
        _str += ", ce={" + PHPZendCEPrinter(self.val['ce']).to_string();
        _str += "}, props={\n\t" +PHPHashTablePrinter(self.val['properties']).to_string()
        _str += "}\n}";
        return _str;
    
    def display_hit(self):
        "return zend_object *"

class PHPZendCEPrinter():
    "print zend_class_entry"

    def __init__(self, val):
        self.val = val;
    
    def to_string(self):
        return "{name=" + PHPZendStringPrinter(self.val['name']).to_string() + "}";
    
    def display_hit(self):
        "return zend_class_entry *"

class PHPZendReferencePrinter():
    "print zend reference"

    def __init__(self, val):
        self.val = val;
    
    def to_string(self):
        return "(REFERENCE) {gc=" + str(self.val['gc']['refcount']) + ", val={\n\t" + PHPZvalPrinter(self.val['val']).to_string()  + "\n}}";
    
    def display_hit(self):
        "return zend_reference *"



class PHPZendStringPrinter():
    "print a zend string"

    def __init__(self, val):
        self.val = val;
    
    #Still need to work on this. cause len is not actual string len
    def to_string(self):
        #if str(self.val.address) == '0x0':
        #    return;
        size = int(self.val['len'])

        #_str = self.val['val'].string('iso8859-1', 'ignore', len);
        #_str = "len = " + str(len);
        _str = ""
        len = 0
        for i in xrange(size):
            if (int(self.val['val'][0]) == 0):
                break;
            else:
                len = len+1;

        if (int(self.val['val'][0]) == 0):
            _str += "nil";
        else:
            _str = self.val['val'].string('iso8859-1', 'ignore', len);

        return "(STRING) {gc=" + str(self.val['gc']['refcount']) + ", size=" +str(size)+ ", [" + _str + "]}"
    
    def display_hint(self):
        return 'zend_string *'


class PHPHashTablePrinter():
    "print a zend hash table"

    def __init__(self, val):
        self.val = val;

    def to_string(self):
        if str(self.val) == '0x0':
            return '0x0';
        nNumOfElements = self.val['nNumOfElements'];
        nTableSize = self.val['nTableSize'];
        nNumUsed = self.val['nNumUsed'];
        try:
            _str = "{nNumUsed = " + str(nNumUsed) + ", nNumOfElements = " + str(nNumOfElements) + ", nTableSize = "+ str(nTableSize) +"}\n";

            pNum = 0;
            #only display 4 elements 
            if (nNumUsed >= 20):
                pNum = 20;
            else:
                pNum = nNumUsed;

            for i in xrange(pNum):
                try:
                    key = self.val['arData'][i]['key'];
                    _str += PHPZendStringPrinter(key).to_string() + " => "
                except:
                    _str += "\t" + str(i) + " => "
                try:
                    val = self.val['arData'][i]['val'];
                    _str += PHPZvalPrinter(val).to_string() + "\n"
                except Exception as i:
                    _str += "unknow";
                    continue;
            return "(HT) " + str(self.val[0].address) + " " + _str;
        except Exception as inst:
            print (type(inst));
            traceback.print_exc(file=sys.stdout)
            #return '(HashT) 0x0'
        
        return "(HashTable) 0x0"
    
    def display_hint(self):
        return 'zend_string *'
        

def zval_lookup_function (val):
    if str(val.type) == "zval *":
        return PHPZvalPrinter(val)
    if str(val.type) == "zend_string *":
        return PHPZendStringPrinter(val)
    #if str(val.type) == "zend_object *":
    #    return PHPZendObjectPrinter(val)
    #if str(val.type) == "HashTable *":
    #    return PHPHashTablePrinter(val)
    return None

gdb.pretty_printers.append(zval_lookup_function)
