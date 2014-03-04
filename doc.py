from xref import Xref
from dictionary import Dictionary
from objects import PdfObject


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

    def fetchObjectByXrefEntry(self, xrefEntry):
        self.filestream.seek(xrefEntry.offset)
        self.filestream.readline()
        obj = PdfObject(self, self.filestream.tell())
        return obj

    def fetchObject(self, num):
        e = self.xref.getEntry(num)
        self.filestream.seek(e.offset)
        self.filestream.readline()
        obj = PdfObject(self, self.filestream.tell())
        return obj
