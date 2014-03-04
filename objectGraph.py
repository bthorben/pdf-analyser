import re
from objects import TYPES


ALL_REFS = re.compile("([0-9]+ [0-9]+ R)")


class Node:
    def __init__(self, xref, obj):
        self.xref = xref
        self.obj = obj
        self.edges = []
        self.findEdges()

    def findEdges(self):
        edges = ALL_REFS.findall(self.xref.content)
        for e in edges:
            ref = e.split()
            self.edges.append(int(ref[0]))

    def getName(self):
        return '%(num)d %(gen)d R' % \
            {'num': self.xref.num, 'gen': self.xref.gen}

    def __str__(self):
        return self.getName() + " -> " + str(self.edges)


class ObjectGraph:
    def __init__(self, doc):
        self.doc = doc
        self.nodes = []
        self.readGraph(doc)

    def readGraph(self, doc):
        for xrefEntry in doc.xref.entries:
            if xrefEntry.state == "f":
                # ignore free entries
                continue
            xrefEntry.load(self.doc.filestream)
            obj = self.doc.fetchObjectByXrefEntry(xrefEntry)
            self.nodes.append(Node(xrefEntry, obj))

    def __str__(self):
        result = 'graph ' + self.doc.file + ' {\n'
        for n in self.nodes:
            if not (n.obj.type == TYPES.DICT or n.obj.type == TYPES.STREAM):
                continue
            namelabel = '"' + n.getName() + '"'
            if n.obj.type == TYPES.DICT:
                namelabel = namelabel + "[color=red"
                if "Type" in n.obj.value:
                    namelabel = namelabel + ' label="' + \
                        str(n.obj.value["Type"]) + '"]'
                elif "FontName" in n.obj.value:
                    namelabel = namelabel + ' label="FontDescriptor"]'
            nodeLine = '\t' + namelabel + ';\n'
            result = result + nodeLine

            for e in n.edges:
                targetNode = self.nodes[e]
                if not (targetNode.obj.type == TYPES.DICT
                        or targetNode.obj.type == TYPES.STREAM):
                    continue
                name = n.getName()
                targetName = targetNode.getName()
                edgeLine = '\t"' + name + '" -> "' + targetName + '";\n'
                result = result + edgeLine

        result = result + "}"
        return result
