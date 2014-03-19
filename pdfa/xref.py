from collections import defaultdict
from xrefEntry import XrefEntry
import hashlib


class Xref:
    def __init__(self, filestream, startxref=None):
        self.filestream = filestream
        self.entries = []
        if not startxref:
            filestream.seek(-150, 2)
            while True:
                line = self.filestream.readline()
                if not line:
                    print "Error: No StartXref found"
                    return
                if "startxref" in line:
                    break
            startxref = int(self.filestream.readline().strip())
        self.startxref = startxref
        self.readXref(startxref)

    def readXref(self, startxref):
        self.filestream.seek(startxref, 0)
        cmd = self.filestream.readline()
        if "obj" in cmd:
            print "Error: Found an xref stream, can't handle that"
            return
        self.filestream.readline()
        linenumber = 0
        for line in self.filestream:
            line = line.strip()
            if not line or line == "trailer":
                break
            e = XrefEntry(linenumber, line.split())
            self.entries.append(e)
            linenumber = linenumber + 1

    def makeRef(self, string):
        if isinstance(string, basestring):
            parts = string.split()
            if len(parts) == 3 and parts[2] is "R":
                return int(parts[0])
        return int(string)

    def getEntry(self, num):
        n = self.makeRef(num)
        return self.entries[n]

    def getOffset(self, num):
        n = self.makeRef(num)
        return self.entries[n].offset

    def getNumberOfEntries(self):
        return len(self.entries)

    def getNumberOfDuplicatedOffsets(self):
        offsets = defaultdict(int)
        duplicateCount = 0
        for e in self.entries:
            if e.state == "f":
                continue
            offsets[e.offset] += 1
            if offsets[e.offset] > 1:
                duplicateCount = duplicateCount + 1
        return duplicateCount

    def getNumberOfDuplicatedContents(self):
        duplicateCount = 0
        contents = defaultdict(int)
        for e in self.entries:
            if e.state == "f":
                continue
            e.load(self.filestream)
            content = e.content
            h = hashlib.sha1(content[100:])
            contents[h] += 1
            if contents[h] > 1:
                duplicateCount = duplicateCount + 1
        return duplicateCount

    def writeTo(self, outputFilestream):
        offset = outputFilestream.tell()
        for e in self.entries:
            if e.state == "f":
                continue
            e.load(self.filestream)
            start = outputFilestream.tell()
            outputFilestream.write(e.content)
            outputFilestream.write("endobj\n\n")
            e.offset = offset
            offset += outputFilestream.tell() - start

        self.startxref = outputFilestream.tell()
        outputFilestream.write("xref\n")
        outputFilestream.write("0 " + str(len(self.entries)) + "\n")
        for e in self.entries:
            outputFilestream.write("%010d %05d %c \n" %
                                   (e.offset, e.gen, e.state))

    def __str__(self):
        xref = "%d entries for objects\n\n" % (len(self.entries) - 1)
        for i in range(0, len(self.entries)):
            e = self.entries[i]
            xref = xref + "%04d: %010d %05d %c \n" % \
                (i, e.offset, e.gen, e.state)
        return xref
