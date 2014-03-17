from argparse import ArgumentParser
import doc
import objectGraph

def __main__:
    parser = ArgumentParser()
    parser.add_argument("pdffile",
                        help="The pdf file to extract the xref from")
    parser.add_argument("-c", "--checkxref",
                        help="Check the xref integrity",
                        action="store_true")
    parser.add_argument("-s", "--show",
                        help="Show the fetched xref-entry with the given number")
    parser.add_argument("-so", "--showobject",
                        help="Show the fetched content that this xref entry \
                        points to")
    parser.add_argument("-r", "--replace",
                        nargs=2,
                        help="Replace the object at the xref-entry with the given \
                        number with the content given by the content of the  \
                        specified file")
    parser.add_argument("-rs", "--replacestream",
                        nargs=2,
                        help="Replace the stream of the object at the xref-entry \
                        with the given number with the content given by the \
                        content of the specified file")
    parser.add_argument("-o", "--output", help="name of the output file")
    parser.add_argument("-g", "--objectgraph",
                        help="Create a graph of all contained objects",
                        action="store_true")
    parser.add_argument("-gc", "--ogc",
                        help="Create a graph of all objects connected to given n",)
    parser.add_argument("-gcr", "--ogcr",
                        help="Create a graph of all objects reverse connected to \
                        given n",)
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
            content = doc.fetchXref(entry).content
            print content,

    if args.showobject:
        args.showobject = splitArg(args.showobject)
        for entry in args.showobject:
            obj = doc.fetchObject(entry)
            print obj,

    if args.replace:
        number = int(args.replace[0])
        replaceFile = args.replace[1]
        if args.output:
            outputFile = args.output
        else:
            outputFile = args.pdffile
        f = open(replaceFile, 'r')
        content = f.read()
        doc.xrefEntry(number).setContent(content)
        o = open(outputFile, 'w')
        doc.writeTo(o)
        o.close()

    if args.replacestream:
        number = int(args.replacestream[0])
        replaceFile = args.replacestream[1]
        if args.output:
            outputFile = args.output
        else:
            outputFile = args.pdffile
        f = open(replaceFile, 'r')
        content = f.read()
        doc.xrefEntry(number).setStreamContent(doc.filestream, content)
        o = open(outputFile, 'w')
        doc.writeTo(o)
        o.close()

    if args.objectgraph:
        graph = objectGraph.ObjectGraph(doc)
        print graph.getFullGraph()

    if args.ogc:
        graph = objectGraph.ObjectGraph(doc)
        print graph.getGraphComponent(int(args.ogc))

    if args.ogcr:
        graph = objectGraph.ObjectGraph(doc)
        print graph.getReversedGraphComponent(int(args.ogcr))
