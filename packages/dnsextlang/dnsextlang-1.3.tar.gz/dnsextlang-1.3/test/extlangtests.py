# 

import unittest
import dnsextlang

dnsdomain='services.net'                # until .arpa works

class LoadDescTests(unittest.TestCase):

    def test_010dns(self):
        " load extlang from the DNS "
        ex = dnsextlang.Extlang(domain=dnsdomain)
        self.assertTrue(ex)
       
    def test_012langdns(self):
        " load extlang from the DNS with language tag "
        ex = dnsextlang.Extlang(domain=dnsdomain, lang='en')
        self.assertTrue(ex)
       
    def test_013nolangdns(self):
        " load extlang from the DNS with language tag that defaults "
        ex = dnsextlang.Extlang(domain=dnsdomain, lang='cn')
        self.assertTrue(ex)
       
    def test_11file(self):
        " load extlang from a file "
        ex = dnsextlang.Extlang(file='rrtypes.txt')
        self.assertTrue(ex)
       
    def test_02dnsrecs(self):
        " simple records from the DNS "        
        ex = dnsextlang.Extlang(domain=dnsdomain)
        self.recs(ex)

    def test_12filerecs(self):
        " simple records from a file "
        ex = dnsextlang.Extlang(file='rrtypes.txt')
        self.recs(ex)
       
    def recs(self, ex):
        " simple records "
        # check that A deparses
        r = dnsextlang.Extrec(ex, string='foo A 1.2.3.4')
        self.assertTrue(r)
        self.assertEqual(str(r).split(), ['foo','A','1.2.3.4'])

        # check that MX deparses and has two fields
        r = dnsextlang.Extrec(ex, string=' MX 1 foo.bar')
        self.assertTrue(r)
        self.assertEqual(str(r)[0], ' ')
        self.assertEqual(str(r).split(), ['MX','1','foo.bar'])
        self.assertEqual(len(r.fields), 2)

        # check that TXT deparses with appropriate quotes
        r = dnsextlang.Extrec(ex, string='a 100 TXT  "able" ba?ker')
        self.assertTrue(r)
        self.assertEqual(str(r).split(), ['a','100','TXT','able','"ba?ker"'])

        # check that BOGUS doesn't parse
        with self.assertRaises(dnsextlang.ExtBadField) as cm:
            dnsextlang.Extrec(ex, string='foo 100 BOGUS 123')

    def test_03dnsforms(self):
        " forms from the DNS "        
        ex = dnsextlang.Extlang(domain=dnsdomain)
        self.forms(ex)

    def test_13fileforms(self):
        " forms from a file "
        ex = dnsextlang.Extlang(file='rrtypes.txt')
        self.forms(ex)
       
    def forms(self, ex):
        " create forms "

        # check that MX turns into a plausible form
        r = dnsextlang.Extrec(ex, string=' MX 1 foo.bar')
        self.assertTrue(r)
        f = r.web_form(prefix='pp')
        self.assertTrue(f)
        self.assertIn('input name="ppname"', f)
        self.assertIn('input name="ppF2"', f)
        self.assertIn('value="foo.bar"', f)

        f = r.web_form(prefix='pp', vert=True)
        self.assertTrue(f)
        self.assertIn('input name="ppname"', f)
        self.assertIn('input name="ppF2"', f)
        self.assertIn('value="foo.bar"', f)

    def test_05dnslist(self):
        " parse a list of records using DNS "        
        ex = dnsextlang.Extlang(domain=dnsdomain)
        self.reclist(ex)

    def test_15filelist(self):
        " parse a list of records using file"        
        ex = dnsextlang.Extlang(file='rrtypes.txt')
        self.reclist(ex)

    def reclist(self, ex):
        " tests for lists of records "
        
        # check comment pseudo form
        cstring = '; software is such sweet sorrow'
        r = dnsextlang.ExtrecList(ex, string=cstring)
        self.assertTrue(r)
        self.assertEqual(len(r), 1)
        self.assertIs(type(r[0]), dnsextlang.ExtComment)
        self.assertEqual(str(r[0]), cstring)
        
        r = dnsextlang.ExtrecList(ex, string='''; software is such sweet sorrow
foo A 100 2.3.4.5
bar SRV 10 20 able.baker
baz SRV 10 20 42 able.baker''')
        self.assertTrue(r)
        self.assertEqual(len(r), 4)
        self.assertIs(type(r[0]), dnsextlang.ExtComment)
        self.assertIs(type(r[1]), dnsextlang.Extrec)
        self.assertIs(type(r[2]), dnsextlang.Extrec)
        self.assertIs(type(r[3]), dnsextlang.Extrec)
        self.assertFalse(r[2].is_valid()) # missing argument
        self.assertTrue(r[3].is_valid())
        

    def test_05dnsformparse(self):
        " parse forms from the DNS "        
        ex = dnsextlang.Extlang(domain=dnsdomain)
        self.formparse(ex)

    def test_16fileformparse(self):
        " parse forms from a file "
        ex = dnsextlang.Extlang(file='rrtypes.txt')
        self.formparse(ex)
       
    def _fpa(self, name, ttl, rrtype, *args, prefix=''):
        " make up a form argument dictionary "
        ad = { "{0}F{1}".format(prefix, seq): str(val) for seq, val in enumerate(args, start=1) }
        ad.update({ prefix+'rrtype': rrtype,
            prefix+'ttl': str(ttl) if type(ttl) is int else ttl,
            prefix+'name': name })
        return ad

    def formparse(self, ex):
        " parse form input "

        # simple MX record
        rr = dnsextlang.Extrec.from_form(ex, self._fpa('foo', 10, 'MX', 100, 'able.baker'))
        self.assertTrue(rr)
        self.assertEqual(str(rr), 'foo 10 MX 100 able.baker')

        # simple MX record with prefix
        rr = dnsextlang.Extrec.from_form(ex, self._fpa('foo', 10, 'MX', 100, 'able.baker', prefix='abc'),
            prefix='abc')
        self.assertTrue(rr)
        self.assertEqual(str(rr), 'foo 10 MX 100 able.baker')

        # bad record type
        with self.assertRaises(dnsextlang.ExtBadField) as cm:
            rr = dnsextlang.Extrec.from_form(ex, self._fpa('foo', 0, 'PARP', 100, 'able.baker'))

        # comment pseudo RR
        rr = dnsextlang.Extrec.from_form(ex, self._fpa(None, None, 'COMMENT', '; where have I heard this?'))
        self.assertTrue(rr)
        self.assertEqual(type(rr), dnsextlang.ExtComment)
