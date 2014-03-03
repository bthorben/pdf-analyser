from argparse import ArgumentParser
from doc import PdfDocument

parser = ArgumentParser()
parser.add_argument("pdffile",
                    help="The pdf file to extract the xref from")
parser.add_argument("-c", "--checkxref",
                    help="Check the xref integrity",
                    action="store_true")
parser.add_argument("-xref", "--xref",
                    help="Show the xref-entry with the given number")
parser.add_argument("-p", "--page",
                    help="Parse the given page")
args = parser.parse_args()

print "Reading", args.pdffile, "...",
doc = PdfDocument(args.pdffile)
print "(total", doc.xref.getNumberOfEntries(), "entries)"

if args.checkxref:
    print "### CHECKING XREF INTEGRITY ###"
    print "Looking for duplicated references ..."
    print "Found", doc.xref.getNumberOfDuplicatedOffsets(), \
        "entries pointing to the same offset"
    print "Looking for duplicated streams ..."
    print "found", doc.xref.getNumberOfDuplicatedContents(), \
        "duplicated contents"

if args.xref:
    if "," in args.show:
        args.show = args.show.split(",")
        args.show = [int(x) for x in args.show]
    else:
        args.show = [int(args.show)]
    for entry in args.show:
        print "### ENTRY", entry, "###"
        e = doc.xref.getEntry(entry)
        print doc.xref.fetch(e)
        print "### END ENTRY", entry, "###"

if args.page:
    print "### PARSING PAGE", args.page, "###"
    print str(doc.trailer.map)
    print str(doc.catalog.map)
