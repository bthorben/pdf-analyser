from xref import Xref
from dictionary import Dictionary
from objects import PdfObject
import StringIO


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

        catalogOffset = self.xref.getOffset(self.trailer.map["Root"])
        self.filestream.seek(catalogOffset)
        self.filestream.readline()
        self.catalog = Dictionary(self.filestream)

    def fetchXref(self, num):
        e = self.xref.getEntry(num)
        e.load(self.filestream)
        return e

    def fetchObject(self, num):
        xrefEntry = self.fetchXref(num)
        xrefEntry.load(self.filestream)
        stream = StringIO.StringIO(xrefEntry.content)
        stream.readline()
        obj = PdfObject(stream, stream.tell())
        return obj

    def fetchObjectFromXref(self, xrefEntry):
        stream = StringIO.StringIO(xrefEntry.content)
        stream.readline()
        obj = PdfObject(stream, stream.tell())
        return obj
