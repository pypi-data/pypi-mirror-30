# dnsextlang records
# Extrec for a single record
# ExtrecMulti and Extreclist for a list of records
# python3 only
# version 1.1

import dns.tokenizer
import dns.rdataclass
import dns.exception

from .exceptions import ExtSyntax, ExtKeytype, ExtBadField, ExtUnimp

from .extfield import ExtFieldS,ExtFieldN, ExtFieldX, ExtFieldA, ExtFieldAA, ExtFieldAAAA, \
    ExtFieldB32, ExtFieldB64, ExtFieldR, ExtFieldT, ExtFieldI1, ExtFieldI2, ExtFieldI4, \
    ExtFieldX6, ExtFieldX8, ExtFieldZ

# patch this table to extend or override field types
fieldclasses = { "S": ExtFieldS, "N": ExtFieldN, "X": ExtFieldX,
    "A": ExtFieldA, "AA": ExtFieldAA, "AAAA": ExtFieldAAAA,
    "B32": ExtFieldB32, "B64": ExtFieldB64, "R": ExtFieldR, "T": ExtFieldT, "Z": ExtFieldZ,
    "I1": ExtFieldI1, "I2": ExtFieldI2, "I4": ExtFieldI4, "X6": ExtFieldX6, "X8": ExtFieldX8
}

class Extrec(object):
    """
    a DNS record parsed with extlang objects
    """
    
    def __init__(self, extlang, string=None, tokens=None, rrtype=None, hasname=True, lineno=1, noinit=False, debug=False):
        """
        turn tokens into list of things and fields
        @param extlang: extlang with the rrtypes
        @type extlang: class Extlang
        @param string: rr text record
        @type string: string
        @param tokens: tokens to parse 
        @type tokens: dns.tokenizer.tokenizer object
        @param rrtype: name of rrtype to create empty record
        @type rrtype str
        @param hasname: whether the record has a name at the beginning
        @type hasname: boolean
        @param lineno: line number in input string where this record started
        @type offset: int
        @type noinit: boolean
        @param noinit: don't do the init, for use in class functions
        """

        if not extlang:
            raise ExtSyntax("need extlang")
        self.extlang = extlang          # where to get the record descriptions from

        self.rr = None
        self.ttl = None                 # optional number
        self.rclass = None              # optional IN or I suppose CH
        self.fields = None
        self.name = None                # record name, will be an "N" type field
        self.lineno = lineno
        self.valid = False
        self.errstr = None

        if noinit:                      # class method will do the rest of the work
            return

        if rrtype:                      # empty record usually for webform
            if string or tokens:
                raise ExtSyntax("string or tokens with specified rrtype")
            self.rr = self.extlang[rrtype]
            if not self.rr:
                raise ExtBadField(rrtype)
            self.fields = self.rr.getfields()
            return

        if string:
            tokens = dns.tokenizer.Tokenizer(string, '<ext string>')
        self.tokens = tokens


        # see if first token is whitespace
        try:
            t = tokens.get(want_leading=True)
        except dns.exception.DNSException as e:
            self.errstr = e.msg
            return

        if t.is_whitespace():
            hasname = False
        else:
            tokens.unget(t)             # put it back for later

        # look for initial name
        if hasname:
            try:
                t = tokens.get()
            except dns.exception.DNSException as e:
                self.errstr = e.msg
                return

            # use fieldclasses in clase name class is overridden
            if "N" not in fieldclasses: # unlikely
                raise ExtUnimp("Name field")

            self.name = fieldclasses["N"]("name", None, None, value=t)

        # check for class and TTL
        while True:
            try:
                t = tokens.get()
            except dns.exception.DNSException as e:
                self.errstr = e.msg
                return

            if t.is_eol_or_eof():
                break;
        
            if t.is_identifier() and t.value.isdigit() and self.ttl is None:
                self.ttl = int(t.value)
                continue

            if self.rclass is None and t.is_identifier():
                try:
                    rclass = dns.rdataclass.from_text(t.value)
                    if not dns.rdataclass.is_metaclass(rclass):
                        self.rclass = t.value
                        continue
                except dns.rdataclass.UnknownRdataclass:
                    pass                # not a class but not an error
            break                       # that's it for TTL and class

        # this should be the rrtype name
        if not t.is_identifier():
            raise ExtSyntax("invalid RRTYPE "+t.value)
        self.rr = self.extlang[t.value]
        if not self.rr:
            raise ExtBadField(t.value)

        # now match up the tokens with the fields
        self.fields = self.rr.getfields()
        for f in self.fields:
            if f.multi:
                toks = []
                while True:
                    try:
                        t = tokens.get()
                    except dns.exception.DNSException as e:
                        self.errstr = e.msg
                        return

                    if t.is_eol_or_eof():
                        break
                    toks.append(t)
                f.parse(toks)
                break
            else:
                try:
                    t = tokens.get()
                except dns.exception.DNSException as e:
                    if e.msg:
                        self.errstr = e.msg
                    else:
                        self.errstr = "Missing items at end of line"
                    return

                if t.is_eol_or_eof():
                    break
                f.parse(t)

        # record is valid if name and all fields are valid
        self.valid = all((f.is_valid() for f in self.fields))
        if self.valid and self.name:
            self.valid = self.name.is_valid()

        # special case for extra data
        if not t.is_eol_or_eof():
            t = tokens.get(want_leading=True) # if last field wasn't multi, see if we're at the end
        if not t.is_eol_or_eof():
            self.valid = False          # extra junk at the end
            self.errstr = "Extra material at end of line"
            while not t.is_eol_or_eof():
                try:
                    t = tokens.get()        # eat the extra junk
                except dns.exception.DNSException as e:
                    self.errstr = e.msg
                    return

    def is_valid(self):
        """
        are all the fields valid
        """
        return self.valid

    def err_str(self):
        """
        error strings from token fails or the fields
        """
        if self.errstr:
            return self.errstr
        e = ", ".join([f.errstr for f in self.fields if (not f.is_valid()) and f.errstr])
        if self.name and not self.name.is_valid():
            ne = self.name.errstr
            if e:
                ne += ", "+e
            return ne
        return e

    def __str__(self):
        """
        turn back into a master file line
        """
        return (str(self.name) if self.name else "  ")+" "+(str(self.ttl)+" " if self.ttl is not None else "")+ \
             (self.rclass+" " if self.rclass else "")+self.rr.rrname+" "+" ".join(map(str,self.fields))


    def web_form(self, prefix='', clform=None, clname=None, clvalue=None, clerrvalue=None, vert=False, ncols=None):
        """
        form, horizontal puts each field on a separate line
        vertical has one row of captions and one of values
        mark error values differently
        added fields for name and TTL, non-editable for rrtype
        optional prefix on each field name
        ncols is max cols in a stack of vertical 

        """
        if clerrvalue is None:
            clerrvalue = clvalue
        
        # hidden thing goes first
        rrtypetag = '<input type="hidden" name="{1}rrtype" value="{0}"/>'.format(self.rr.rrname, prefix)
        fields = []
        # make list of (tag, value, valid) triples, format horiz or
        # vert later

        # fakeish fields for the name and rrtype
        fields.append(("Name", """<input name="{1}name" type="text" size="100" value="{0}" />""".format(str(self.name) if self.name else "", prefix),
            True))
        fields.append(("Type", self.rr.rrname, True))
        fields.append(("TTL", """<input name="{1}ttl" type="text" value="{0}" />""".format("" if self.ttl is None else self.ttl, prefix),
            True))

        # number the input fields in case of lame names

        fields += [f.formed(name="{1}F{0}".format(n, prefix)) for n,f in enumerate(self.fields, start=1)]

        if vert:
            # two row vertical version
            td1 = "".join("<td{0}>{1}</td>".format(_cl(clname), n) for n, d, v in fields) # names on the first row
            row1 = "<tr{0}>{1}</tr>".format(_cl(clform), td1) 
            td2 = "".join("<td{0}>{1}</td>".format(_cl(clvalue if v else clerrvalue), d) for n, d, v in fields)
            row2 = "<tr{0}>{1}</tr>".format(_cl(clform), td2) # two row form
            return "\n".join((rrtypetag, row1, row2))
        else: 
            # two column horizontal version
            rows = "\n".join("<tr{0}><td{1}>{2}</td><td{3}>{4}</td></tr>".format(_cl(clform), _cl(clname), n,
                _cl(clvalue if v else clerrvalue), d) for n, d, v in fields)
            return "\n".join((rrtypetag, rows))

    @classmethod
    def from_form(cls, extlang, formdata, prefix=""):
        """
        parse up form data into an extrec
        @param extlang: extlang with the rrtypes
        @type extlang: class Extlang
        @param formdata: dict of form values
        @type formdata: dict
        keys are rrtype, name (record name), ttl, F1, F2, ...
        """

        if prefix+"rrtype" not in formdata:
            raise ExtSyntax("no RRTYPE")

        # special hack for comments
        if formdata[prefix+'rrtype'] == 'COMMENT':
            string = formdata.get(prefix+'F1', "")
            if string.strip() and string.strip()[0] != ';': # should be blank or comment
                errstr = "Not a comment"
            else:
                errstr = None
            return ExtComment(extlang, string=string, lineno=1, errstr=errstr)

        # make a new instance
        self = cls(extlang, noinit=True)

        self.rr = self.extlang[formdata[prefix+'rrtype']]
        if not self.rr:                 # no such rrtype
            raise ExtBadField(formdata[prefix+'rrtype'])

        if prefix+'ttl' in formdata and formdata[prefix+'ttl'].isdigit():
            self.ttl = int(formdata[prefix+'ttl'])
        else:
            self.ttl = None                 # optional number

        if prefix+'name' in formdata and formdata[prefix+'name'].strip() > '':
            ns = formdata[prefix+'name'].strip()
            try:
                t = dns.tokenizer.Token(dns.tokenizer.IDENTIFIER, ns, ('\\' in ns))
            except dns.exception.DNSException as e:
                raise ExtSyntax(e.msg)

            if "N" not in fieldclasses: # unlikely
                raise ExtUnimp("Name field")
            self.name = fieldclasses["N"]("name", None, None, value=t)
        else:
            self.name = None                # record name

        self.lineno = None

        self.fields = self.rr.getfields()

        for n,f in enumerate(self.fields, start=1):
            fn = '{1}F{0}'.format(n, prefix)
            if fn not in formdata:
                raise ExtSyntax("No field "+fn)
            tokens = dns.tokenizer.Tokenizer(formdata[fn], filename='<field {0}>'.format(f.name))
            if f.multi:
                toks = []
                while True:
                    try:
                        t = tokens.get()
                    except dns.exception.UnexpectedEnd as e:
                        raise ExtSyntax(e.msg)
                        
                    if t.is_eol_or_eof():
                        break
                    toks.append(t)
                f.parse(toks)
            else:
                try:
                    t = tokens.get()
                except dns.exception.DNSException as e:
                    raise ExtSyntax(e.msg)

                if not t.is_eol_or_eof():
                    f.parse(t)
                    try:
                        t = tokens.get()
                    except dns.exception.DNSException as e:
                        raise ExtSyntax(e.msg)

            if not t.is_eol_or_eof():
                f.valid = False
                f.errstr = "junk at end of field"
                f.value = formdata[fn]  # so user can try again

        self.valid = all((f.is_valid() for f in self.fields))
        if self.valid and self.name:
            self.valid = self.name.is_valid()
        return self

def _cl(fcl):
    """
    html class reference or nothing
    """
    return " class="+fcl if fcl else ""

class ExtComment(Extrec):
    """
    mutant extrec for comment lines or invalid stuff
    """

    def __init__(self, extlang, string=None, lineno=1, errstr=None, debug=False):
        super().__init__(extlang, lineno=lineno, debug=debug, noinit=True)
        self.comment = string       # just a comment string
        self.errstr = errstr
        self.valid = not errstr         # valid if no error

    def err_str(self):
        return self.errstr

    def __str__(self):
        return self.comment

    def web_form(self, prefix='', clform=None, clname=None, clvalue=None, clerrvalue=None, vert=False, ncols=None):
        """
        one field either way
        """
        rrtypetag = '<input type="hidden" name="{1}rrtype" value="{0}"/>'.format("COMMENT", prefix)
        fn = "Error" if self.errstr else "Comment"
        cif = """<input name="{0}F1" type="text" size="100" value="{1}" />""".format(prefix,
        "" if self.comment is None else self.comment.replace('"', '&quot;').replace('\\','&#092;'))
        if vert:
            if ncols:
                td1 = """<td{0} colspan="{1}">{2}</td>""".format(_cl(clname), ncols, fn)
            else:
                td1 = "<td{0}>{1}</td>".format(_cl(clname), fn)
            row1 = "<tr{0}>{1}</tr>".format(_cl(clform), td1) 
            if ncols:
                td2 = """<td{0} colspan="{1}">{2}</td>""".format(_cl(clvalue), ncols, cif)
            else:
                td2 = """<td{0}>{1}</td>""".format(_cl(clvalue), cif)
            row2 = "<tr{0}>{1}</tr>".format(_cl(clform), td2) # two row form
            return "\n".join((rrtypetag, row1, row2))
        else:
            # two column horizontal version
            rows = """<tr{0}><td{1}>&nbsp;</td><td{2}>{3}</td></tr>""".format(_cl(clform), _cl(clname), _cl(clvalue), cif)
            return "\n".join((rrtypetag, rows))



################################################################
class ExtrecMulti(object):
    """
    a list of DNS record Extrec's parsed from a single string
    throws out comments, recovers poorly from syntax errors
    but does handle multi-line RRs
    """
    
    def __init__(self, extlang, string=None, tokens=None, lineno=1, debug=False, noinit=False):
        """
        parse up the string into potentially multiple records
        and return a list of Extrec's

        @param string: rr text record
        @type string: string
        @param tokens: tokens to parse 
        @type tokens: dns.tokenizer.tokenizer object
        @param lineno: line number in input string where this record started
        @type offset: int
        """

        self.extlang = extlang          # where to get the record descriptions from
        self.lineno = lineno
        self.valid = False               # turned off in case of error
        self.errstr = None
        self.recs = []
        if noinit:                      # for subclasses
            return

        if string:
            tokens = dns.tokenizer.Tokenizer(string, '<ext string>')
        while True:
            # skip blank lines, also stop on EOF
            while not tokens.eof:
                try:
                    t = tokens.get(want_leading=True)
                except dns.exception.DNSException as e:
                    self.errstr = e.msg
                    return

                if not t.is_eol_or_eof():
                    tokens.unget(t)
                    break
            if tokens.eof:
                break                  # it's an interface now
            
            if debug:
                print("lineno", tokens.where())
            try:
                xr = Extrec(extlang, tokens=tokens, lineno=tokens.where()[1], debug=debug) # line number
            except ExtSyntax as e:
                self.errstr = e.msg
                return

            if not xr:
                break
            self.recs.append(xr)
            if tokens.eof:
                break                  # it's an interface now
        self.valid = True               # parse worked, recs might be bad

    def is_valid(self):
        return self.valid and all((r.is_valid() for r in self.recs))

    def err_str(self):
        """
        error strings from token fails or the fields
        """
        e = ", ".join([r.err_str() for r in self.recs if r.err_str()])
        if self.errstr:
            return self.errstr + ", "+e
        return e

    def __str__(self):
        """
        new line seprated string
        """
        return "\n".join(str(r) for r in self.recs)

    def __getitem__(self, key):
        """
        return Nth item from the list
        @param key item to return
        @type key int
        """
        if type(key) is not int:
            raise ExtKeytype(key)
        return self.recs[key]

    def __len__(self):
        return len(self.recs)

    def append(self, rec):
        """
        add a new extrec, looks list a list

        @param rec Extrec to add
        @type rec Extrec
        """
        if type(rec) is not Extrec:
            raise ExtKeytype(rec)
        self.recs.append(rec)

class ExtrecList(ExtrecMulti):
    """
    a list of DNS record Extrec's parsed from a single string
    split into lines
    doesn't handle multi-line RRs but saves comments
    """
    
    def __init__(self, extlang, string=None, lineno=1, debug=False):
        super().__init__(extlang, lineno=lineno, debug=debug, noinit=True)

        for n,l in enumerate(string.splitlines(), start=1):
            if debug:
                print("parse",n,l)
            if not l.strip() or l.strip()[0] == ';': # blank or comment
                xr = ExtComment(extlang, string=l, lineno=n, debug=debug)
            else:
                try:
                    xr = Extrec(extlang, string=l, lineno=n, debug=debug)
                except (ExtSyntax, ExtBadField) as e:
                    xr = ExtComment(extlang, string=l, lineno=n, errstr=e.msg, debug=debug)
            self.recs.append(xr)
        self.valid = True               # parse worked, recs might be bad
