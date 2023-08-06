# extlang field types
# python3 only
# version 1.1

import re
from .exceptions import ExtSyntax, ExtKeytype, ExtBadField, ExtUnimp

class Extfield(object):
    """
    base for various field types
    value is string or int, multi field fields as string value
    """
    fieldtype = None

    def __init__(self, name, quals, comment, value=None):
        self.name = name
        self.quals = quals
        self.comment = comment
        self.value = None               # set in individual routines
        self.multi = False              # takes multiple arguments
        self.valid = False              # doesn't have valid data
        self.errstr = "Field missing"   # why it didn't like the data

    def is_valid(self):
        """
        is this field valid
        """
        return self.valid

    def is_multi(self):
        """
        does this field take mutiple arguments?
        """
        return self.multi

    def __repr__(self):
        return '<ExtField {} {}>'.format(self.fieldtype, self)

    def __str__(self):
        if self.value is None:
            return '???'
        return str(self.value)

    def parse(self, tok):
        """
        takes a dnspython token or list of tokens
        validates and stores string or number in self.value
        """        
        raise ExtUnimp(self.name)
        
    def _qu(self, tok):
        """
        token value, quoted if has funky chars, space separated if more than one
        """
        if type(tok) is list:
            return " ".join([self._qu(x) for x in tok])

        if re.match(r'^[-0-9a-zA-Z:./_=\\]+$', tok.value):
            return tok.value
        else:
            return '"'+str(tok.value)+'"'

    def formed(self, name=None):
        """
        default HTML form (name, input field, validflag) to plug into tables
        name is field name for input field
        validflag is for coloring tables
        xxx need to escape wonky values
        """
        return ("{0}<br/>{1}".format(self.name, self.errstr) if self.errstr else self.name,
            '<input name="{0}" type="text" size="100" value="{1}" />'.format(name if name else self.name,
                "" if self.value is None else str(self).replace('"', '&quot;').replace('\\','&#092;')),
            self.valid)

class ExtFieldS(Extfield):
    """
    single or multiple string
    need to be smarter about escaping
    """
    fieldtype = "S"
    def __init__(self, name, quals, comment, value=None):
        super().__init__(name, quals, comment, value)

        if quals and "M" in quals:
            self.multi = True
        if value:
            self.parse(value)           # set value
            
    def parse(self, toks):
        self.value = self._qu(toks)             # anything goes for now
        self.valid = True
        return True


class ExtFieldI(Extfield):
    """
    integer fields of various types
    value is a string in case of symbolic values
    """

    fieldlen = 0                    # size of I1, I2, I4

    def __init__(self, name, quals, comment, value=None):
        super().__init__(name, quals, comment, value)
        if quals:                       # NAME=val, ...
            self.codes = dict( q.split('=') for q in quals.split(','))
        else:
            self.codes = None

        if value:
            self.parse(value)           # set value
    
    def parse(self, tok):
        """
        parse an input token
        returns True or False
        sets errstr if parse failed
        """

        self.valid = False
        self.value = tok.value                # save so user can edit it
        if not tok.is_identifier():
            self.errstr = "Number needed"
            return False

        if not tok.value.isdigit():     # check for symbolic types
            if self.codes and tok.value in self.codes:
                self.valid = True
                return True
            else:
                self.errstr = "Must be a number"
            return False

        i = int(tok.value)
        if i >= (1 << (8*self.fieldlen)):
            self.errstr = "Number too large for field"
            return False

        self.valid = True
        return True

class ExtFieldI1(ExtFieldI):
    fieldtype = "I1"
    fieldlen = 1

class ExtFieldI2(ExtFieldI):
    fieldtype = "I2"
    fieldlen = 2

class ExtFieldI4(ExtFieldI):
    fieldtype = "I4"
    fieldlen = 4

class ExtFieldN(Extfield):
    """
    domain name
    """

    fieldtype = "N"
    # pattern for a DNS name, with \nnn octal escapes
    _namepattern = re.compile(r"""[*0-9a-z_] ((\\[0-7]{3}|[-0-9a-z_])*(\\[0-7]{3}|[0-9a-z_])?)
        (\.(\\[0-7]{3}|[0-9a-z_])((\\[0-7]{3}|[-0-9a-z_])*(\\[0-7]{3}|[0-9a-z_])?))* \.?|\.""",
        re.I|re.X)

    def __init__(self, name, quals, comment, value=None):
        super().__init__(name, quals, comment, value)
        if quals and "O" in quals:
            self.multi = True           # optional name

        if value:
            self.parse(value)           # set value
                
    def parse(self, tok):
        """
        parse an input domain name
        returns True or False
        sets errstr if parse failed
        """

        self.valid = False
        self.errstr = None
        if self.multi:
            if not tok:                 # optional name not there
                self.value = None
                self.valid = True
                return True
            if len(tok) > 1:
                self.errstr = "Extra junk at end of record"
            tok = tok[0]                # use first token which should be the only one

        self.value = tok.value                # save so user can edit it
        if not tok.is_identifier():
            self.errstr = "Domain name needed"
            return False
        r = self._namepattern.fullmatch(tok.value) # close enough
        if r:
            if not self.errstr:         # might be junk
                self.valid = True
        else:
            self.errstr = "Not a domain name"
        return self.valid

    def __str__(self):
        """
        none is valid if it's multi
        """        
        if self.value is None and not self.multi:
            return '???'
        return str(self.value)


class ExtFieldR(Extfield):
    """
    rrtype or R[L] list of rrtypes
    """

    fieldtype = "R"

    def __init__(self, name, quals, comment, value=None):
        super().__init__(name, quals, comment, value)
        if quals:
            if "L" == quals:
                self.multi = True
            else:
                raise ExtBadField(fieldtype)
        if value:
            self.parse(value)           # set value
                
    def parse(self, toks):
        """
        parse an input token
        returns True or False
        sets errstr if parse failed
        must be rrtype(s)
        """

        self.valid = True
        self.value = ""                # save so user can edit it
        for t in toks:
            if not t.is_identifier():
                self.errstr = "RR type name needed"
                self.valid = False
            r = re.match('^[a-z][a-z0-9]*$', t.value, flags=re.A|re.I)
            if not r:
                self.errstr = "Not a RR type name"
                self.valid = False
            self.value += t.value+" "
        if self.value == "":
            self.valid = False
            self.errstr = "Need RR type names"
        return self.valid

class ExtFieldX(Extfield):
    """
    hex strings of various sorts
    """

    fieldtype = "X"

    def __init__(self, name, quals, comment, value=None):
        super().__init__(name, quals, comment, value)
        self.multi = True
        if quals:
            if "C" == quals:
                self.multi = False
            else:
                raise ExtBadField(fieldtype)
        if value:
            self.parse(value)           # set value
                
    def parse(self, tok):
        """
        parse an input token
        returns True or False
        sets errstr if parse failed
        must be hex string(s)
        """

        self.valid = True
        self.value = ""                # save so user can edit it
        for t in tok:
            self.value += t.value+" "
            if not t.is_identifier():
                self.errstr = "Hex string needed"
                self.valid = False
            r = re.match('^[0-9a-f]+$', t.value, flags=re.A|re.I)
            if not r:
                self.errstr = "Not a hex string"
                self.valid = False
        if self.value == "":
            self.errstr = "Hex string needed"
            self.valid = False
        return self.valid

class ExtFieldXn(Extfield):
    """
    X6 or X8 fixed length hex
    """

    fieldtype = "Xn"
    fieldlen = 0                     # will be overridden

    def __init__(self, name, quals, comment, value=None):
        super().__init__(name, quals, comment, value)
        if quals:
                raise ExtBadField(fieldtype)
        if value:
            self.parse(value)           # set value
                
    def parse(self, tok):
        """
        parse an input token
        returns True or False
        sets errstr if parse failed
        must be hex string(s)
        """

        self.valid = False
        self.value = tok.value                # save so user can edit it
        if not tok.is_identifier():
            self.errstr = "Hex bytes needed"
            return False
        r = re.match(r'[0-9a-f]{2}(-[0-9a-f]{2})+$', self.value, flags=re.I)
        if not r:
            self.errstr = "Hypen separated hex bytes needed"
            return False
        if len(self.value) != (self.fieldlen*3)-1:
            self.errstr = "Must be {0} bytes long".format(self.fieldlen)
            return False
        self.valid = True
        return True

class ExtFieldX6(ExtFieldXn):
    fieldtype = "X6"
    fieldlen = 6
            
class ExtFieldX8(ExtFieldXn):
    fieldtype = "X8"
    fieldlen = 8

class ExtFieldB32(Extfield):
    """
    base32 string value
    """

    fieldtype = "B32"
                
    def __init__(self, name, quals, comment, value=None):
        super().__init__(name, quals, comment, value)

        if value:
            self.parse(value)           # set value

    def parse(self, tok):
        """
        parse an input token list
        returns True or False
        sets errstr if parse failed
        must be base32
        """
        self.valid = False
        self.value = tok.value                # save so user can edit it
        if not tok.is_identifier():
            self.errstr = "String needed"
            return False
        r = re.match(r'^[a-z2-7]+={0,6}$', tok.value, flags=re.A|re.I)
        if r:
            self.valid = True
        else:
            self.errstr = "Bad base32 data"
        return self.valid


class ExtFieldB64(Extfield):
    """"
    base64 binary field, always last can be multiple groups
    """

    fieldtype = "B64"
    def __init__(self, name, quals, comment, value=None):
        super().__init__(name, quals, comment, value)
        self.multi = True
        if value:
            self.parse(value)           # set value
                
    def parse(self, tok):
        """
        parse an input token list
        returns True or False
        sets errstr if parse failed
        must be base64
        """
        self.valid = False
        if not all((t.is_identifier() for t in tok)):
            self.errstr = "String needed"
            return False

        self.value = "".join((t.value for t in tok))
        r = re.match(r'^[0-9a-zA-Z+/]+\={0,2}$', self.value, flags=re.A)
        if r:
            self.valid = True
        else:
            self.errstr = "Bad base64 data"
        return self.valid

class ExtFieldA(Extfield):
    """
    IPv4 address
    """

    fieldtype = "A"
                
    def __init__(self, name, quals, comment, value=None):
        super().__init__(name, quals, comment, value)

        if value:
            self.valid = self.parse(value)           # set value

    def parse(self, tok):
        """
        parse an input token
        returns True or False
        sets errstr if parse failed
        must be IPv4 address n.n.n.n
        """

        self.value = tok.value                # save so user can edit it
        self.valid = False
        if not tok.is_identifier():
            self.errstr = "IPv4 address needed"
            return False

        r = re.match(r'^(\d+)\.(\d+)\.(\d+)\.(\d+)$', tok.value, flags=re.A)
        if not r:
            self.errstr = "Bad IPv4 format"
            return False
        for oc in r.group(1,2,3,4):
            if int(oc) > 255:
                self.errstr = "Bad octet"
                return False
        self.valid = True
        return True

def v6check(s):
    """
    check if s looks like part of a v6 address
    return number of groups
    or None if it's not valid
    """
    if s == '':
        return 0
    
    ss = s.split(':')
    for g in ss:
        r = re.match(r'^[0-9a-f]{1,4}$', g, flags=re.A|re.I)
        if not r:
            return None
    return len(ss)

class ExtFieldAA(Extfield):
    """
    half a v6 address
    """

    fieldtype = "AA"
                
    def __init__(self, name, quals, comment, value=None):
        super().__init__(name, quals, comment, value)

        if value:
            self.parse(value)           # set value

    def parse(self, tok):
        """
        parse an input token
        returns True or False
        sets errstr if parse failed
        must be half a v6 address
        """
        self.valid = False
        self.value = tok.value                # save so user can edit it
        if not tok.is_identifier():
            self.errstr = "String needed"
            return False
        c = v6check(tok.value)
        if not c or c > 4:
            self.errstr = "Not an AA value"
            return False
        self.value = True
        return True


class ExtFieldAAAA(Extfield):
    """"
    v6 addresss
    """
    
    fieldtype = "AAAA"
                
    def __init__(self, name, quals, comment, value=None):
        super().__init__(name, quals, comment, value)

        if value:
            self.parse(value)           # set value

    def parse(self, tok):
        """
        parse an input token
        returns True or False
        sets errstr if parse failed
        must be a v6 address
        """
        self.valid = False
        self.value = tok.value                # save so user can edit it
        if not tok.is_identifier():
            self.errstr = "String needed"
            return False
        ss = tok.value.split('::')
        if len(ss) == 1:                # nothing elided
            c = v6check(tok.value)
            if c != 8:
                self.errstr = "Invalid IPv6 address"
                return False
        elif len(ss) == 2:
            c1 = v6check(ss[0])
            c2 = v6check(ss[1])
            if c1 is None or c2 is None or c1+c2 > 7:
                self.errstr = "Invalid IPv6 address" # must elide at least one
                return False
        else:
            self.errstr = "Invalid IPv6 address" # empty or ::::
            return False

        self.valid = True
        return True

class ExtFieldT(Extfield):
    """
    timestamp
    """

    fieldtype = "T"
                
    def __init__(self, name, quals, comment, value=None):
        super().__init__(name, quals, comment, value)

        if value:
            self.parse(value)           # set value

    def parse(self, tok):
        """
        parse an input token
        returns True or False
        sets errstr if parse failed
        """

        self.valid = False
        self.value = tok.value
        if not tok.is_identifier():
            self.errstr = "String needed"
            return False

        if not tok.value.isdigit():
            self.errstr = "Must be a number"
            return False

        if len(tok.value) <= 10:
            if int(tok.value) >= (1 << 32): 
                self.errstr = "Time value too large for field"
            else:
                self.valid = True
        elif len(tok.value) == 14:
                self.valid = True       # timestamp

        return self.valid

class ExtFieldZ(Extfield):
    """
    stub for exotic types
    """

    fieldtype = "Z"
