# dns extension language
# handle extlang record database
# python3 only
# version 1.1

import re
import dns.resolver

from .exceptions import ExtSyntax, ExtKeytype, ExtBadField, ExtUnimp

from .extrec import fieldclasses
from .extfield import ExtFieldZ            # default field type

class Extlang(object):
    """
    DNS extension language class
    can load from a file or from the DNS

    create with Extlang(file="foo.txt", domain="arpa", lang="en", resolver=None)
    only one of file or domain, resolver used to look up types in the domain,
    defaults to an ordinary resolver

    rrs is one dict, indexed by number for rrtype and by string for mnemonic
    """

    # match head record, $1 = name, $2 = number, $3 = description
    headpattern = re.compile(r"""^ (?P<rname>[a-z0-9][-a-z0-9]*):(?P<rtype>\d+)
        (?: : (?P<rqual>[a-z]+) )?
        (?: \s+ (?P<rcomment>.*))?$""", re.I|re.X)


    # match a field, $1 = type, $2 = quals, $3 - name, $4 = comment
    fieldpattern = re.compile(r"""^ (?P<type>I[124]|AA?|AAAA|[ZNRSTX]|B32|B64|T6|X[68]) # field type
	(?:\[ (?P<quals> (?:[CALOMX]|[-a-zA-Z0-9]+=\d+|WKS|NSAP|NXT|A6[PS]|APL|IPSECKEY|HIPHIT|HIPPK)
        (?:,(?:[CALMX]|[-a-zA-Z0-9]+=\d+))* )\])? # optional qualifiers
	(?: :(?P<name>[-a-zA-Z0-9]+))?	# optional field name
	(?: \s+ (?P<comment>.*))?""", re.I|re.X)	# optional comment

    def __init__(self, file=None, domain=None, lang=None, resolver=None):
        if file and domain:
            print("extlang: cannot have both file and domain")
            return None

        if not file and not domain:
            print("extlang: must provide file or domain")
            return None

        self.file = file
        self.domain = domain            # base for rrtype.domain or rrname.domain
        self.lang = lang                # language tag
        self.resolver = resolver
        self.rrs = dict()

        if file:
            try:
                self._loadfile(file)
            except FileNotFoundError:
                print("extlang: no file",file)
                return None
        if domain:
            if self.resolver is None:
                self.resolver = dns.resolver.Resolver()

    def _stash(self, rtype, rname, rqual, rcomment, fields):
        """
        save an extlang description under rtype (int) and rname (string)
        """

        r = Extlangrr(rtype, rname, rqual, rcomment, fields)
        self.rrs[int(rtype)] = r
        self.rrs[rname] = r
        return r

    def _loadfile(self, file):
        """
        read in rrtype descriptions from a file, put them in self.fields
        """
        rtype = None
        rname = None
        rqual = None
        rcomment = None
        fields = []

        with open(file, "r") as f:
            for l in f:
                if re.match(r'\s*(#|$)', l):
                    continue                    # comment
                l = l.rstrip()
                # new RR
                r = self.headpattern.fullmatch(l)
                if r:
                    if fields:
                        self._stash(rtype, rname, rqual, rcomment, fields)
                    rname = r.group('rname')
                    rtype = r.group('rtype')
                    rqual = r.group('rqual')
                    rcomment = r.group('rcomment')
                    fields = []
                    continue

                if not l[:1].isspace(): # field records start with spaces
                    raise ExtSyntax(l)
                    
                r = self.fieldpattern.fullmatch(l.strip())
                if r:
                    fields.append({ d:r.group(d) for d in ('type','quals','name','comment')})
                else:
                    raise ExtSyntax(l)

        if fields:
            self._stash(rtype, rname, rqual, rcomment, fields)
        

    def __getitem__(self, key):
        """ get an extlang object by int rrtype or string name
        if it's from a file or it's in self.fields, just return it
        if it's from the DNS, try to fetch it if it's not there
        """
        if type(key) is str:
            key = key.upper()
        if key in self.rrs:
            return self.rrs[key];
        if self.file:
            return None                 # not there

        # try and get it from the DNS
        if type(key) == int:
            dname = "{0}.rrtype.{1}".format(key, self.domain)
        elif type(key) is str:
            dname = "{0}.rrname.{1}".format(key, self.domain)
        else:
            raise ExtKeytype(key)
        if self.lang:
            nolangdname = dname
            dname = self.lang+"."+dname

        descrrs = None
        try:
            descrrs = self.resolver.query(dname, 'TXT')
        except (dns.resolver.Timeout, dns.resolver.NXDOMAIN, dns.resolver.YXDOMAIN,
            dns.resolver.NoAnswer, dns.resolver.NoNameservers):

            if self.lang:               # try without the language tag
                try:
                    descrrs = self.resolver.query(nolangdname, 'TXT')
                except (dns.resolver.Timeout, dns.resolver.NXDOMAIN, dns.resolver.YXDOMAIN,
                    dns.resolver.NoAnswer, dns.resolver.NoNameservers):
                    self.rrs[key] = None     # don't look again, should do TTL timeout I suppose
                    return None
            else:
                self.rrs[key] = None     # don't look again, should do TTL timeout I suppose
                return None

     
        for r in descrrs.rrset:
            s = [t.decode() for t in r.strings]
            if len(s) < 3 or s[0] != "RRTYPE=1":
                continue
            rp = self.headpattern.fullmatch(s[1])
            if not rp:
                raise ExtSyntax(s[1])

            rname = rp.group('rname').upper()
            rtype = int(rp.group('rtype'))
            rqual = rp.group('rqual')
            rcomment = rp.group('rcomment')

            # check that we got the right one
            if type(key) == int:
                if int(rtype) != key:
                    raise ExtSyntax(s[1])
            else:
                if rname != key:
                    raise ExtSyntax(s[1])

            fields = []

            for f in s[2:]:
                rp = self.fieldpattern.fullmatch(f)
                if not rp:
                    raise ExtSyntax(f)
                fields.append( { d:rp.group(d) for d in ('type','quals','name','comment')})

            return self._stash(rtype, rname, rqual, rcomment, fields)

        # no match
        self.rrs[key] = None
        return None

    def getfields(self, key):
        """
        get a list of field class structures for an rrtype
        """
        r = self[key]
        if not r:
            return None
        return r.getfields()

    def rrnames(self, select=None, obsolete=False):
        """
        all of the rrnames
        perhaps with the experimental and obsolete ones
        as a list or as an HTML <select>
        file returns what we have, DNS looks up _LIST
        select arg is the name of the field
        """
        if self.file:
            l = [k for k in self.rrs.keys() if type(k) is str] # names are all strings
        else:
            try:
                rrs = self.resolver.query("_LIST.RRNAME."+self.domain, 'TXT')
            except (dns.resolver.Timeout, dns.resolver.NXDOMAIN, dns.resolver.YXDOMAIN,
                dns.resolver.NoAnswer, dns.resolver.NoNameservers):
                return None
     
            for r in rrs.rrset:
                s = [t.decode() for t in r.strings]
                if len(s) >= 2 or s[0] == "RRTYPE=1":
                    l = s[1:]
                    break
            else:
                return None             # no DNS match
            
        if not obsolete:                # remove experimental and obsolete ones
            l = [ rr for rr in l if not "O" in self.rrs[rr].rrqual and not "E" in self.rrs[rr].rrqual ]

        l.sort()
        if not select:
            return l

        # HTML select
        o = "\n".join("<option>{0}</option>".format(r) for r in l)
        return '<select name="{0}" size="1">\n{1}\n</select>\n'.format(select, o)

    def rrtypes(self, select=None, obsolete=False):
        """
        all of the rrtypes
        perhaps with the experimental and obsolete ones
        as a list or as an HTML <select>
        file returns what we have, DNS looks up _LIST of names
        select arg is the name of the field
        """
        l = self.rrnames(obsolete=obsolete)

        if not l:
            return None

        # turn into numbers
        l = [ self.rrs[rr].rrtype for rr in l ]
        l.sort()
        if not select:
            return l

        # HTML select
        o = "\n".join("<option>{0}</option>".format(r) for r in l)
        return '<select name="{0}" size="1">\n{1}\n</select>\n'.format(select, o)

class Extlangrr(object):
    """
    a single rrtype
    create with Extlangrr(123, 'ABC', 'A', 'doc text', [fields])

    @param rrtype: RR type numner
    @type rrtype: number
    @param rrname: RR type name
    @type rrname: string
    @type rrqual: string or null
    @param rrqual: rrtype qualifiers
    @param rrcomment: description
    @type rrcomment: string
    @param fields: fields in the RR
    @type fields: list of Extfield

    @rtype: Extlangrr object
    """

    def __init__(self, rrtype, rrname, rrqual, rrcomment, fields):
        self.rrtype = int(rrtype)
        self.rrname = rrname
        self.rrqual = rrqual
        self.rrcomment = rrcomment
        self.fields = fields

    def __repr__(self):
        return '<Extlangrr {} {}>'.format(self.rrname, ",".join([f['name'] for f in self.fields]))
    
    def getfields(self):
        """
        get a list of field class structures for an rr
        unknown field types default to Z
        """
        return [ fieldclasses.get(p['type'], ExtFieldZ)(p['name'],p['quals'],p['comment'])
            for p in self.fields ]
