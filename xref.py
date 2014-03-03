from collections import defaultdict
import hashlib


class Entry:
    def __init__(self, line):
        self.offset = int(line[0])
        self.gen = int(line[1])
        self.state = line[2]
        self.content = ""


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
        for line in self.filestream:
            line = line.strip()
            if not line:
                break
            e = Entry(line.split())
            self.entries.append(e)

    def makeRef(self, string):
        parts = string.split()
        if len(parts) == 3 and parts[2] is "R":
            return int(parts[0])
        else:
            return int(string)

    def getEntry(self, num):
        return self.entries[self.makeRef(num)]

    def fetch(self, e):
        self.filestream.seek(e.offset, 0)
        content = ""
        line = self.filestream.readline()
        while line and not "endobj" in line:
            content = content + line
            line = self.filestream.readline()
        return content

    def getNumberOfEntries(self):
        return len(self.entries)

    def getNumberOfDuplicatedOffsets(self):
        offsets = defaultdict(int)
        duplicateCount = 0
        for e in self.entries:
            if e.state == "n":
                continue
            offsets[e.offset] += 1
            if offsets[e.offset] > 1:
                duplicateCount = duplicateCount + 1
        return duplicateCount

    def getNumberOfDuplicatedContents(self):
        duplicateCount = 0
        contents = defaultdict(int)
        for e in self.entries:
            if e.state == "n":
                continue
            content = self.fetch(e)
            h = hashlib.sha1(content[100:])
            contents[h] += 1
            if contents[h] > 1:
                duplicateCount = duplicateCount + 1
        return duplicateCount
