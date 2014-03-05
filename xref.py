from collections import defaultdict
import hashlib


class Entry:
    def __init__(self, num, line):
        self.num = num
        self.offset = int(line[0])
        self.gen = int(line[1])
        self.state = line[2]
        self.content = ""
        self.loaded = False

    def load(self, filestream):
        if self.loaded:
            return
        filestream.seek(self.offset, 0)
        lines = []
        line = filestream.readline()
        while line and not "endobj" in line:
            lines.append(line)
            line = filestream.readline()
        self.content = "".join(lines)
        self.loaded = True


class Xref:
    def __init__(self, filestream, startxref):
        self.filestream = filestream
        self.startxref = startxref
        self.entries = []
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
            if not line:
                break
            e = Entry(linenumber, line.split())
            self.entries.append(e)
            linenumber = linenumber + 1

    def makeRef(self, string):
        if isinstance(string, basestring):
            parts = string.split()
            if len(parts) == 3 and parts[2] is "R":
                return int(parts[0])
        return int(string)

    def getEntry(self, num):
        return self.entries[self.makeRef(num)]

    def getOffset(self, num):
        return self.entries[self.makeRef(num)].offset

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
