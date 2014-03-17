import string
import re
import logging


logging.basicConfig(level=logging.DEBUG)
REF = re.compile("^\s*[0-9]+ [0-9]+ R")

TYPE_CHARS = "/[]<>"


class TYPES:
    BOOL = 1
    NUM = 2
    STRING = 3
    BSTRING = 4
    NAME = 5
    ARRAY = 6
    DICT = 7
    STREAM = 8
    REF = 9
    NULL = 10


class PdfObject:
    def __init__(self, stream, offset=0):
        self.stream = stream
        self.offset = offset
        self.parse()

    def __str__(self):
        if self.type == TYPES.DICT:
            output = []
            output.append("<<\n")
            for key, value in self.value.iteritems():
                output.append("/" + key + " ")
                output.append(str(value))
                output.append("\n")
            output.append(">>\n")
            return "".join(output)
        elif self.type == TYPES.ARRAY:
            output = []
            output.append("[")
            for value in self.value:
                output.append(str(value))
            output.append("]")
            return "".join(output)
        elif self.type == TYPES.NUM:
            numStr = str(self.value)
            return numStr.replace(".0", "")
        elif self.type == TYPES.STRING:
            return "(" + str(self.value) + ")"
        else:
            return str(self.value)

    def parse(self):
        self.stream.seek(self.offset, 0)
        self.value = self.consumeValue()

    def consumeValue(self):
        curChar = self.stream.read(1)
        while curChar in string.whitespace:
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
            currentPosition = self.stream.tell()
            ahead = curChar + self.stream.read(32)
            self.stream.seek(currentPosition)
            match = REF.search(ahead)
            if match is not None:
                self.type = TYPES.REF
                ref = match.group(0)
                self.stream.seek(len(ref) - 1, 1)
                return match.group(0)
            else:
                self.type = TYPES.NUM
                return self.consumeNumber(curChar)
        if curChar == "(":
            self.type = TYPES.STRING
            return self.consumeUntil(')')
        if curChar == "/":
            self.type = TYPES.NAME
            return "/" + self.consumeName()
        if curChar == "[":
            self.type = TYPES.ARRAY
            return self.consumeArray()
        if curChar == "<":
            nextChar = self.stream.read(1)
            if nextChar == "<":
                self.type = TYPES.DICT
                return self.consumeDict()
            else:
                self.type = TYPES.BSTRING
                self.stream.seek(-1, 1)
                return "<" + self.consumeUntil('>') + ">"
        # should not happen
        self.debug(curChar)

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

    def consumeName(self):
        name = ""
        curChar = self.stream.read(1)
        while (curChar not in string.whitespace) and \
              (curChar not in TYPE_CHARS):
            name = name + curChar
            curChar = self.stream.read(1)
        self.stream.seek(-1, 1)
        return name

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
            elif curChar is None:
                break
            else:
                data = data + curChar
            if data.endswith(">>"):
                break
            if curChar == "/":
                dictKey = self.consumeDictKey()
                dictValue = PdfObject(self.stream, self.stream.tell())
                value[dictKey] = dictValue
                data = ""
        return value

    def consumeDictKey(self):
        key = ""
        curChar = self.stream.read(1)
        while (curChar not in string.whitespace) and \
              (curChar not in TYPE_CHARS):
            key = key + curChar
            curChar = self.stream.read(1)
        self.stream.seek(-1, 1)
        return key

    def debug(self, curChar):
        currentPosition = self.stream.tell()
        self.stream.seek(-300, 1)
        length = self.stream.tell() - currentPosition
        context = self.stream.read(length)
        context = context + "###" + curChar + "###"
        self.stream.seek(1, 1)
        context = context + self.stream.read(299)
        print("Error: can't read object, curChar: " + curChar +
              "\ncontext\n" + context)
        import pdb
        pdb.set_trace()
