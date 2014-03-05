import string
import re
import logging


logging.basicConfig(level=logging.DEBUG)
REF = re.compile("^\s*[0-9]+ [0-9]+ R")


class TYPES:
    BOOL = 1
    NUM = 2
    STRING = 3
    NAME = 4
    ARRAY = 5
    DICT = 6
    STREAM = 7
    REF = 8
    NULL = 9


class PdfObject:
    def __init__(self, stream, offset):
        self.stream = stream
        self.offset = offset
        self.parse()

    def __str__(self):
        return str(self.value)

    def parse(self):
        self.stream.seek(self.offset, 0)
        self.value = self.consumeValue()

    def consumeValue(self):
        curChar = self.stream.read(1)
        if curChar == "n":
            self.type = TYPES.NULL
            self.stream.read(3)
            return "null"
        if curChar == "t":
            self.type = TYPES.BOOL
            self.stream.read(3)
            return True
        if curChar == "f":
            self.type = TYPES.BOOL
            self.stream.read(4)
            return False
        if curChar.isdigit() or curChar == "-":
            ahead = curChar + self.stream.read(50)
            self.stream.seek(-(len(ahead) - 1), 1)
            match = REF.search(ahead)
            if match is not None:
                self.type = TYPES.REF
                ref = match.group(0)
                self.stream.seek(len(ref), 1)
                return match.group(0)
            else:
                self.type = TYPES.NUM
                return self.consumeNumber(curChar)
        if curChar == "(":
            self.type = TYPES.STRING
            return self.consumeUntil(')')
        if curChar == "/":
            self.type = TYPES.STRING
            return self.consumeUntil(string.whitespace)
        if curChar == "[":
            self.type = TYPES.ARRAY
            return self.consumeArray()
        if curChar == "<":
            nextChar = self.stream.read(1)
            if nextChar == "<":
                self.type = TYPES.DICT
                return self.consumeDict()
            else:
                self.type = TYPES.STRING
                self.stream.seek(-1, 1)
                return self.consumeUntil('>')
        self.stream.seek(-300, 1)
        context = self.stream.read(299)
        context = context + "###" + curChar + "###"
        self.stream.seek(1, 1)
        context = context + self.stream.read(299)
        print("Error: can't read object, curChar: " + curChar +
              "\ncontext\n" + context)
        import pdb
        pdb.set_trace()

    def consumeUntil(self, endChar):
        string = ""
        lastChar = ""
        curChar = self.stream.read(1)
        while True:
            if curChar in endChar and not ((lastChar + curChar) == '\\)'):
                break
            string = string + curChar
            lastChar = curChar
            curChar = self.stream.read(1)
        return string

    def consumeNumber(self, curChar):
        numberString = ""
        while curChar.isdigit() or curChar == "-" or curChar == ".":
            numberString = numberString + curChar
            curChar = self.stream.read(1)
        try:
            number = float(numberString)
            return number
        except Exception:
            print "not a number: ", numberString

    def consumeArray(self):
        array = []
        while True:
            curChar = self.stream.read(1)
            if curChar in string.whitespace:
                continue
            if curChar == "]":
                return array
            array.append(PdfObject(self.stream, self.stream.tell() - 1))

    def consumeDict(self):
        value = {}
        data = ""
        while True:
            curChar = self.stream.read(1)
            if curChar in string.whitespace:
                continue
            else:
                data = data + curChar
            if data.endswith(">>"):
                break
            if curChar == "/":
                dictKey = ""
                curChar = self.stream.read(1)
                while curChar not in string.whitespace:
                    dictKey = dictKey + curChar
                    curChar = self.stream.read(1)
                dictValue = PdfObject(self.stream, self.stream.tell())
                value[dictKey] = dictValue
                data = ""
        return value

    def consumeDictKey(self):
        key = ""
        curChar = self.stream.read(1)
        while curChar not in string.whitespace:
            key = key + curChar
            curChar = self.stream.read(1)
        return key
