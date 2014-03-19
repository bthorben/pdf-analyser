from xref import Xref
from objects import PdfObject, TYPES
import StringIO


class FileHeader:
    def __init__(self, filestream):
        lineOne = filestream.readline()
        lineTwo = filestream.readline()
        self.content = "".join([lineOne, lineTwo])


class Trailer:
    def __init__(self, filestream):
        filestream.seek(-300, 2)
        while True:
            line = filestream.readline()
            if not line:
                print "Error: Trailer found"
                return
            if "trailer" in line:
                break
        self.start = filestream.tell()
        self.dict = PdfObject(filestream, filestream.tell())


class PdfDocument:
    def __init__(self, pdffile):
        self.file = pdffile
        self.filestream = open(pdffile, "r")
        self.trailer = None
        self.xref = None
        self.process()

    def process(self):
        self.header = FileHeader(self.filestream)
        self.trailer = Trailer(self.filestream)
        self.xref = Xref(self.filestream)

    def xrefEntry(self, num):
        return self.xref.getEntry(num)

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

    def fetchStream(self, num):
        xrefEntry = self.fetchXref(num)
        xrefEntry.load(self.filestream)
        stream = StringIO.StringIO(xrefEntry.content)
        stream.readline()
        obj = PdfObject(stream, stream.tell())
        if obj.type == TYPES.STREAM:
            return obj.content
        else:
            return "no stream, is", obj.type

    def fetchObjectFromXref(self, xrefEntry):
        stream = StringIO.StringIO(xrefEntry.content)
        stream.readline()
        obj = PdfObject(stream, stream.tell())
        return obj

    def writeTo(self, filestream):
        filestream.write(self.header.content)
        filestream.write("\n")
        self.xref.writeTo(filestream)
        filestream.write("\ntrailer\n")
        filestream.write(str(self.trailer.dict))
        filestream.write("\nstartxref\n")
        filestream.write(str(self.xref.startxref))
        filestream.write("\n%%EOF")
