import sys
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
    def __init__(self, doc, offset):
        self.doc = doc
        self.offset = offset
        self.parse()

    def __str__(self):
        return str(self.value)

    def parse(self):
        self.doc.filestream.seek(self.offset, 0)
        self.value = self.consumeValue()

    def consumeValue(self):
        curChar = self.doc.filestream.read(1)
        if curChar == "n":
            self.type = TYPES.NULL
            self.doc.filestream.read(3)
            return "null"
        if curChar == "t":
            self.type = TYPES.BOOL
            self.doc.filestream.read(3)
            return True
        if curChar == "f":
            self.type = TYPES.BOOL
            self.doc.filestream.read(4)
            return False
        if curChar.isdigit() or curChar == "-":
            ahead = curChar + self.doc.filestream.read(50)
            self.doc.filestream.seek(-50, 1)
            match = REF.search(ahead)
            if match is not None:
                self.type = TYPES.REF
                ref = match.group(0)
                self.doc.filestream.seek(len(ref), 1)
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
            nextChar = self.doc.filestream.read(1)
            if nextChar == "<":
                self.type = TYPES.DICT
                return self.consumeDict()
            else:
                self.type = TYPES.STRING
                self.doc.filestream.seek(-1, 1)
                return self.consumeUntil('>')
        self.doc.filestream.seek(-100, 1)
        context = self.doc.filestream.read(99)
        context = context + "###" + curChar + "###"
        self.doc.filestream.seek(1, 1)
        context = context + self.doc.filestream.read(99)
        print("Error: can't read object, curChar: " + curChar +
              "\ncontext\n" + context)
        print int("-kl")
        sys.exit()

    def consumeUntil(self, endChar):
        string = ""
        curChar = self.doc.filestream.read(1)
        while curChar not in endChar:
            string = string + curChar
            curChar = self.doc.filestream.read(1)
        return string

    def consumeNumber(self, curChar):
        numberString = ""
        while curChar.isdigit() or curChar == "-" or curChar == ".":
            numberString = numberString + curChar
            curChar = self.doc.filestream.read(1)
        try:
            number = float(numberString)
            return number
        except Exception:
            self.doc.filestream.seek(-50, 1)
            print "not a number: ", numberString, "\n", \
                self.doc.filestream.read(100)

    def consumeArray(self):
        array = []
        while True:
            curChar = self.doc.filestream.read(1)
            if curChar in string.whitespace:
                continue
            if curChar == "]":
                return array
            array.append(PdfObject(self.doc, self.doc.filestream.tell() - 1))

    def consumeDict(self):
        value = {}
        data = ""
        while True:
            curChar = self.doc.filestream.read(1)
            if curChar in string.whitespace:
                continue
            else:
                data = data + curChar
            if data.endswith(">>"):
                break
            if curChar == "/":
                dictKey = ""
                curChar = self.doc.filestream.read(1)
                while curChar not in string.whitespace:
                    dictKey = dictKey + curChar
                    curChar = self.doc.filestream.read(1)
                dictValue = PdfObject(self.doc, self.doc.filestream.tell())
                value[dictKey] = dictValue
                data = ""
        return value

    def consumeDictKey(self):
        key = ""
        curChar = self.doc.filestream.read(1)
        while curChar not in string.whitespace:
            key = key + curChar
            curChar = self.doc.filestream.read(1)
        return key
