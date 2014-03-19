pdf-analyser
============

A PDF Analyser written in Python. It enables you to make basic xref integrity
checks, view objects, replace objects and output the complete objects or just
components to .dot files

    usage: pdfAnalyser [-h] {check, show, replace, graph} ... pdffile

## Options

* `check` check the xref table for duplicates (entries and references streams)
* `show` display the xref, an object or the content of a stream
```
objectnumber  The object number to show
-x, --xref    Show the xref
-s, --stream  Show the (if possible) decompressed stream
```
* `replace` replace an object or stream
```
objectnumber  The number of the object to replace
input         The file to load the data to replace the object with
output        Where to write the pdf with the replaced object
--stream      replace just the stream, not the whole object (if possible)
```
* `graph` display the object graph in the dot-format
```
-f FROMOBJECT, --fromObject FROMOBJECT
                      Only consider objects reachable from here
-t TOOBJECT, --toObject TOOBJECT
                      Only consider objects that lead to here
```
* `[-h]` help with the commands