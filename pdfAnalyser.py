from argparse import ArgumentParser
import doc
import objectGraph

parser = ArgumentParser()
parser.add_argument("pdffile",
                    help="The pdf file to extract the xref from")
parser.add_argument("-c", "--checkxref",
                    help="Check the xref integrity",
                    action="store_true")
parser.add_argument("-s", "--show",
                    help="Show the fetched xref-entry with the given number")
parser.add_argument("-sc", "--showcontent",
                    help="Show the fetched content that this xref entry \
                    points to")
parser.add_argument("-p", "--page",
                    help="Parse the given page")
parser.add_argument("-g", "--objectgraph",
                    help="Create a graph of all contained objects",
                    action="store_true")
args = parser.parse_args()


def splitArg(string):
    if "," in string:
        return [int(x) for x in string.split(",")]
    else:
        return [int(string)]


doc = doc.PdfDocument(args.pdffile)

if args.checkxref:
    print "### CHECKING XREF INTEGRITY ###"
    print "Looking for duplicated references ..."
    print "Found", doc.xref.getNumberOfDuplicatedOffsets(), \
        "entries pointing to the same offset"
    print "Looking for duplicated streams ..."
    print "found", doc.xref.getNumberOfDuplicatedContents(), \
        "duplicated contents"

if args.show:
    args.show = splitArg(args.show)
    for entry in args.show:
        print "### OBJECT", entry, "###"
        obj = doc.fetchObject(entry)
        print obj
        print "### END OBJECT", entry, "###"

if args.showcontent:
    args.showcontent = splitArg(args.showcontent)
    for entry in args.showcontent:
        print "### CONTENT OF ", entry, "###"
        content = doc.fetchXref(entry).content
        print content
        print "### END CONTENT", entry, "###"

if args.page:
    print "### PARSING PAGE", args.page, "###"
    print str(doc.trailer.map)
    print str(doc.catalog.map)

if args.objectgraph:
    graph = objectGraph.ObjectGraph(doc)
    print str(graph)
