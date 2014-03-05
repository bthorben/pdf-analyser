pdf-analyser
============

A relatively simple PDF analyser written in Python. It was created to analyse issues we had with PDF.js. Currently it can only handles uncompressed PDF files. 

    usage: pdfAnalyser.py [-h] [-c] [-s SHOW] [-o SHOWOBJECT] 
                      [-g] [-gc OGC] [-gcr OGCR]
                      pdffile

## Options

* `[-h]` help
* `[-c]` check the xref table for duplicates (entries and references streams)
* `[-s SHOW]` show the content of an object as references by e.g. `560 0 R`
* `[-o SHOWOBJECT]` like show, but prints the parsed object
* `[-g]` print a DOT-format graph of all objects as nodes and their references as edges
* `[-g OGC]` as -g but only showing all objects reachable from given object
* `[-gcr OGCR]` as -g but only showing all objects that lead to given object
