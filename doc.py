from xref import Xref
from objects import Dictionary


class PdfDocument:
    def __init__(self, pdffile):
        self.file = pdffile
        self.filestream = open(pdffile, "r")
        self.trailer = None
        self.xref = None
        self.process()

    def process(self):
        self.filestream.seek(-300, 2)
        while True:
            line = self.filestream.readline()
            if not line:
                print "Error: Trailer found"
                return
            if "trailer" in line:
                break
        self.trailer = Dictionary(self.filestream)

        while True:
            line = self.filestream.readline()
            if not line:
                print "Error: No StartXref found"
                return
            if "startxref" in line:
                break
        xrefoffset = int(self.filestream.readline().strip())
        self.xref = Xref(self.filestream, xrefoffset)

        print "yes"
        print self.trailer.map
        catalogOffset = self.xref.getEntry(self.trailer.map["Root"]).offset
        print "catOffset", catalogOffset
        self.filestream.seek(catalogOffset)
        self.filestream.readline()
        self.catalog = Dictionary(self.filestream)
