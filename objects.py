import sys
import string


class Dictionary:
    def __init__(self, filestream, pos=None):
        self.filestream = filestream
        self.map = {}
        if pos is not None:
            self.filestream.seek(pos)
        self.parse()

    def parse(self):
        data = self.filestream.read(2)
        if not "<<" in data:
            sys.exit("Wrong dictionary syntax, <<: " + data)
        data = ""
        while True:
            curChar = self.filestream.read(1)
            if curChar in string.whitespace:
                continue
            else:
                data = data + curChar
            if data.endswith(">>"):
                break
            if curChar == "/":
                key = self.consumeKey()
                value = self.consumeValue()
                self.map[key] = value
                data = ""

    def consumeKey(self):
        key = ""
        curChar = self.filestream.read(1)
        while curChar in string.whitespace:
            key = key + curChar
            curChar = self.filestream.read(1)
        return key

    def consumeValue(self):
        value = ""
        curChar = self.filestream.read(1)
        # TODO: correctly parse all the other objects (arrays, strings, etc)
        arrLevel = 0
        while True:
            if curChar == "[":
                arrLevel = arrLevel + 1
            if curChar == "]":
                arrLevel = arrLevel + 1
            if curChar == "\n" and arrLevel == 0:
                self.filestream.seek(-1, 1)
                break
            if value.endswith(">>"):
                self.filestream.seek(-3, 1)
                break
            value = value + curChar
            if value.endswith("<<"):
                return Dictionary(self.filestream,
                                  self.filestream.tell() - 2)
            curChar = self.filestream.read(1)
        return value
