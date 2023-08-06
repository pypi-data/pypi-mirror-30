#!/usr/bin/env python3
# convert between DNS zone and file format of dnsextlang data
# version 1.0

import dnsextlang
import argparse
import sys
import re

parser = argparse.ArgumentParser(description='DNS extension language format converter')
parser.add_argument('--file', action='store', help="Input file");
parser.add_argument('--domain', action='store', help="Input domain");
parser.add_argument('--namezone', action='store', help="File for zone of rrname records");
parser.add_argument('--typezone', action='store', help="File for zone of rrtype records");
parser.add_argument('--lang', action='store', help="Language tag for zones");
parser.add_argument('--outfile', action='store', help="File to write");
parser.add_argument('--obs', action='store_true', help="Include obsolete and experimental types");

args = parser.parse_args()

if args.file:
    if args.domain:
        print("Must specify one of --file or --zone")
        exit(1)
    ex = dnsextlang.Extlang(file=args.file)
elif args.domain:
    ex = dnsextlang.Extlang(domain=args.domain, lang=args.lang)
else:
    print("Must specify --file or --zone")
    exit(1)

if not ex:
    print("Bad file or domain")

# open requisite files
if not (args.namezone or args.typezone or args.outfile):
    print("No output requested.")
    exit(1)

if args.namezone:
    try:
        namezone = open(args.namezone, "w")
    except:
        print("cannot open",namezone)
        exit(1)
else:
    namezone = None

if args.typezone:
    try:
        typezone = open(args.typezone, "w")
    except:
        print("cannot open",typezone)
        exit(1)
else:
    typezone = None

if args.outfile:
    try:
        outfile = open(args.outfile, "w")
    except:
        print("cannot open",outfile)
        exit(1)
else:
    outfile = None

names = ex.rrnames(obsolete=args.obs)
print("get types")
types = ex.rrtypes(obsolete=args.obs)


if args.namezone:
    print("; Machine generated rrname description zone", file=namezone)
    print('''_LIST TXT "RRTYPE=1"'''," ".join(names), file=namezone)
    
if args.typezone:
    print("; Machine generated rrtype description zone", file=typezone)
    print('''_LIST TXT "RRTYPE=1"'''," ".join(map(str,types)), file=typezone)
    
if args.outfile:
    print("# Machine generated rr description file", file=outfile)
    
for name in names:
    # make first rrtype line
    rr = ex[name]
    rrn = "{0}:{1}".format(rr.rrname, rr.rrtype)
    if rr.rrqual:
        rrn += ":{0}".format(rr.rrqual)
    if rr.rrcomment:
        rrn += " "+rr.rrcomment

    # make per field lines
    fl = []
    for f in rr.getfields():
        if f.quals:
            fn = "{0}[{1}]:{2}".format(f.fieldtype, f.quals, f.name)
        else:
            fn = "{0}:{1}".format(f.fieldtype, f.name)
        if f.comment:
            fn += " "+f.comment
        fl.append(fn)

    # print them out as a file
    if args.outfile:
        print(rrn, file=outfile)
        for fn in fl:
            print("  ",fn, file=outfile)
        print("", file=outfile)

    # print TXT record and CNAME if needed
    if args.namezone:
        if args.lang:
            n = "{0}.{1}".format(args.lang, rr.rrname)
        else:
            n = rr.rrname
        print('''{0} TXT "RRTYPE=1" "{1}"'''.format(n, rrn),
            " ".join(['"{0}"'.format(fn.replace('"', '\\"')) for fn in fl]), file=namezone)
        if args.lang:
            print('''{0} CNAME {1}'''.format(rr.rrname, n), file=namezone)

    if args.typezone:
        if args.lang:
            n = "{0}.{1}".format(args.lang, rr.rrtype)
        else:
            n = rr.rrtype
        print('''{0} TXT "RRTYPE=1" "{1}"'''.format(n, rrn),
            " ".join(['"{0}"'.format(fn.replace('"', '\\"')) for fn in fl]), file=typezone)
        if args.lang:
            print('''{0} CNAME {1}'''.format(rr.rrtype, n), file=typezone)
