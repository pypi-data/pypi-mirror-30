================
 DNS Extension Language Parser and HTML Helper, Version 1.2
================

This package implements the DNS extension language described in
draft-levine-dnsextlang.  Each DNS rrtype has a description as
a list of typed fields with descriptions.  The package can
read the descriptions from a local file or from the DNS.

Classes
------------

Extlang
  A set of rrtype definitions loaded from a file or the DNS.

Extrec
  A single DNS record, with or without parsed content.  Can turn a record into an HTML form,
  and can turn the list of values from a form back into an Extrec.

ExtComment
  A fake record for a comment line in a master file.

ExtRecMulti
  A list of Extrec's parsed from a string that is a chunk of a master file.  Can handle
  multi-line records, but has poor error recovery.

ExtRecList
  A list of Extrec's parsed from a string, with each line parsed separately.  Can't handle
  multi-line records, but has better error recovery.


DNS sources
------------

The draft says that the DNS descriptions will come from RRTYPE.ARPA and RRNAME.ARPA.
Until that happens, which may be a while, descriptions are available at RRTYPE.SERVICES.NET
and RRNAME.SERVICES.NET. 


John Levine, johnl@taugh.com, May 2017
