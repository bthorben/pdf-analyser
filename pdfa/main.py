from argparse import ArgumentParser
import doc
import objectGraph


def splitArg(string):
    if ',' in string:
        return [int(x) for x in string.split(',')]
    else:
        return [int(string)]


def check(args):
    document = doc.PdfDocument(args.pdffile)
    print '### CHECKING XREF INTEGRITY ###'
    print 'Looking for duplicated references ...'
    print 'Found', document.xref.getNumberOfDuplicatedOffsets(), \
        'entries pointing to the same offset'
    print 'Looking for duplicated streams ...'
    print 'found', document.xref.getNumberOfDuplicatedContents(), \
        'duplicated contents'


def show(args):
    document = doc.PdfDocument(args.pdffile)

    if not args.objectnumber:
        return
    numbers = splitArg(args.objectnumber)
    showstream = args.stream
    for number in numbers:
        if showstream:
            try:
                content = document.fetchStream(number)
            except Exception:
                print "Object doesn't seem to be a stream"
                return
        else:
            content = document.fetchXref(number).content
        print content,


def showxref(args):
    document = doc.PdfDocument(args.pdffile)
    print '### XREF ###'
    print str(document.xref)


def replace(args):
    objectnumber = int(args.objectnumber)
    input_filename = args.input
    output_filename = args.output
    replace_stream = args.stream

    input_file = open(input_filename, 'r')
    output_file = open(output_filename, 'w')
    content = input_file.read()
    document = doc.PdfDocument(args.pdffile)
    if replace_stream:
        document.xrefEntry(objectnumber).setStreamContent(document.filestream,
                                                          content)
    else:
        document.xrefEntry(objectnumber).setContent(content)
    document.writeTo(output_file)
    output_file.close()


def graph(args):
    document = doc.PdfDocument(args.pdffile)
    component_from = args.fromObject
    component_to = args.toObject

    graph = objectGraph.ObjectGraph(document)
    if component_from:
        print graph.getGraphComponent(int(component_from))
    elif component_to:
        print graph.getReversedGraphComponent(int(component_to))
    else:
        print graph.getFullGraph()


def main():
    parser = ArgumentParser(prog='pdfAnalyser')
    subparsers = parser.add_subparsers(title='commands')

    # check
    subp = subparsers.add_parser('check',
                                 help='Check the xref integrity')
    subp.set_defaults(func=check)

    # show
    subp = subparsers.add_parser('show',
                                 help='Show one or more objects')
    subp.add_argument('objectnumber', default=1,
                      help='The object number to show')
    subp.add_argument('-s', '--stream',
                      help='Show the (if possible) decompressed stream',
                      action='store_true')
    subp.set_defaults(func=show)

    # showxref
    subp = subparsers.add_parser('showxref',
                                 help='Show the xref')
    subp.set_defaults(func=showxref)

    # replace
    subp = subparsers.add_parser('replace',
                                 help='Replace an object')
    subp.add_argument('objectnumber', type=int, default=None,
                      help='The number of the object to replace')
    subp.add_argument('--stream',
                      help='replace just the stream, not the whole object\
                      (if possible)',
                      action='store_true')
    subp.add_argument('input',
                      help='The file to load the data to replace the object \
                      with')
    subp.add_argument('output',
                      help='Where to write the pdf with the replaced object')
    subp.set_defaults(func=replace)

    # graph
    subp = subparsers.add_parser('graph',
                                 help='Print the objectgraph as .dot file')
    subp.add_argument('-f', '--fromObject', type=int,
                      help='Only consider objects reachable from here')
    subp.add_argument('-t', '--toObject',
                      help='Only consider objects that lead to here')
    subp.set_defaults(func=graph)

    # pdffile
    parser.add_argument('pdffile',
                        help='The pdf file to extract the xref from')

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
