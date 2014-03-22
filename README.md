pdfAnalyser
============

A PDF Analyser written in Python. It enables you to make basic xref integrity
checks, view objects, replace objects and output the complete objects or just
components to .dot files

    usage: pdfAnalyser [-h] {check, show, replace, graph} ... pdffile

Note: This tool only supports documents with xref-tables and without object 
streams, i.e. "uncompressed" documents. You can produce such documents e.g. 
with `mutools` with `mutools clean -d [pdffile]`

## Getting started

To get an overview of the document you can start having a look at the 
xref-table by typing

```
$ pdfa showxref pdffile.pdf
```

### Showing and Replacing

You can view any object of this xref that has an `n` in it's entry 
(meaning it is used) by typing it's number like this:
```
$ pdfa show 8 pdffile.pdf
```

If you then see this object is a stream you can just show this stream by 
adding `--stream`, which is useful to export the stream, e.g.:
```
$ pdfa show 8 --stream pdffile.pdf > 8.stream
```
This stream is automatically uncompressed if it was encoded with 
FlateDecode.

A common usecase would be to edit `8.stream` now and replace the original
content with your new file by
```
$ pdfa replace 8 8.stream pdffile_8replaced.pdf --stream pdffile.pdf
```

### Using the Graph

Another good way to get an overview is to export the object-graph of the
document as a .dot file (and viewing it in a good viewer, have a look at
wikipedias .dot 
[article](http://en.wikipedia.org/wiki/DOT_(graph_description_language))).

Export the graph by typing
```
$ pdfa graph pdffile.pdf > pdffile_graph.dot
```

## Options

* `check` check the xref table for duplicates (entries and references streams)
* `showxref` display the xref-table
* `show` display an object or the content of a stream
```
objectnumber  The object number to show
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
