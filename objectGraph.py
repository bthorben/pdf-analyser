import re
from objects import TYPES


ALL_REFS = re.compile("([0-9]+ [0-9]+ R)")


class Node:
    def __init__(self, xref, obj):
        self.xref = xref
        self.obj = obj
        self.edges = []
        self.incomingEdges = []
        self.findEdges()
        self.visited = False

    def addIncomingEdge(self, e):
        self.incomingEdges.append(e)

    def findEdges(self):
        edges = ALL_REFS.findall(self.xref.content)
        for e in edges:
            ref = e.split()
            self.edges.append(int(ref[0]))

    def getType(self):
        type = "T" + str(self.obj.type)
        if self.obj.type == TYPES.DICT:
            if "Type" in self.obj.value:
                type = str(self.obj.value["Type"])
            elif "FontName" in self.obj.value:
                type = "FontDescriptor"
        return type

    def getName(self):
        return '%(num)d %(gen)d R' % \
            {'num': self.xref.num, 'gen': self.xref.gen}

    def getNameLabel(self, labelDict):
        l = [(str(x) + '="' + str(labelDict[x]) + '"') for x in labelDict]
        return str(self.xref.num) + "[" + " ".join(l) + "]"

    def getGraphString(self):
        nodeType = self.getType()
        attr = {}
        attr["label"] = str(self.xref.num) + ' ' + nodeType
        if nodeType in ["Page", "Pages", "Catalog"]:
            attr["color"] = "green"
        elif nodeType in ["Font", "FontDescriptor"]:
            attr["color"] = "red"
        elif not nodeType in ["T1", "T2", "T3", "T4", "T5", "T8", "T9"]:
            attr["color"] = "blue"

        result = '\t' + self.getNameLabel(attr) + ';\n'
        for e in self.edges:
            edgeLine = '\t' + str(self.xref.num) + ' -> ' + str(e) + ';\n'
            result = result + edgeLine

        return result

    def __str__(self):
        return self.getRef() + " -> " + str(self.edges)


class ObjectGraph:
    def __init__(self, doc):
        self.doc = doc
        self.nodes = {}
        self.readGraph(doc)

    def readGraph(self, doc):
        for xrefEntry in doc.xref.entries:
            if xrefEntry.state == "f":
                # ignore free entries
                continue
            xrefEntry.load(self.doc.filestream)
            obj = self.doc.fetchObjectFromXref(xrefEntry)
            self.nodes[xrefEntry.num] = Node(xrefEntry, obj)

    def getReversedGraphComponent(self, num):
        for n in self.nodes:
            for e in self.nodes[n].edges:
                self.nodes[e].addIncomingEdge(n)
        nodeList = [num]
        q = [num]
        numFontMet = 0
        while len(q) > 0:
            c = q.pop(0)
            self.nodes[c].visited = True
            for e in self.nodes[c].incomingEdges:
                if self.nodes[c].getType() == "Font":
                    numFontMet = numFontMet + 1
                    if numFontMet > 3:
                        break
                if not self.nodes[e].visited:
                    nodeList.append(e)
                    q.append(e)
        return self.getDotFromNodeList(nodeList)

    def getGraphComponent(self, num):
        nodeList = [num]
        q = [num]
        while len(q) > 0:
            c = q.pop(0)
            for e in self.nodes[c].edges:
                if e not in nodeList:
                    nodeList.append(e)
                    q.append(e)
        return self.getDotFromNodeList(nodeList)

    def getFullGraph(self):
        return self.getDotFromNodeList(self.nodes)

    def getDotFromNodeList(self, list):
        result = 'graph ' + self.doc.file + ' {\n'
        for n in list:
            result = result + self.nodes[n].getGraphString()
        result = result + "}"
        return result
