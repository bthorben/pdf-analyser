from objects import PdfObject


class XrefEntry:
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

    def setContent(self, content):
        self.content = content
        self.loaded = True

    def setStreamContent(self, filestream, content):
        try:
            filestream.seek(self.offset, 0)
            filestream.readline()
            streamDict = PdfObject(filestream, filestream.tell())
            streamDict.value["Length"] = len(content)
            if "Filter" in streamDict.value:
                streamDict.value.pop("Filter", None)
            out = []
            out.append("%d %d obj" % (self.num, self.gen))
            out.append("\n")
            out.append(streamDict.printDict())
            out.append("stream\n")
            out.append(content)
            out.append("\nendstream\n")
            self.content = "".join(out)
            self.loaded = True
        except Exception, e:
            print "can't set stream content of " + str(self)
            raise e
