#!/usr/bin/env python
# -*- coding: utf-8 -*-

## improve: http://stackoverflow.com/questions/1871524/convert-from-json-to-csv-using-python
## http://trac.wildfiregames.com/browser/ps/trunk/source/tools/templatesanalyzer/unitTables.py

import numpy as np
import xml.etree.ElementTree as ET
import sys, os, glob, json

sys.dont_write_bytecode = True

folders = [
  ["", "all"],
  ["carthaganians", "cart"],
  ["celts", "celt"],
  ["hellenes", "hele"],
  ["mauryans", "maur"],
  ["persians", "pers"],
  ["romans", "roma"],
  ["successors", ""],
]


def floatOrString(param) :
  try :
    return float(param)
  except :
    return param


def ReadTechnology(root, pathfileTemplate):

if __name__ == '__main__':

  print
  trunk = '/Daten/Projects/Osiris/ps/trunk'
  rootExport = '/home/noiv/.local/share/0ad/mods/public/simulation/ai/hannibal/explorer/data/'
  rootTemplates = trunk + '/binaries/data/mods/public/simulation/templates/'

  for export in exports : 

    dataExports = {}
    pathExports = rootTemplates + export + "/"
    templates   = glob.glob(pathExports + '*.xml')
    fileExport  = rootExport + export + "-json.export"

    for template in templates :
      pathfile = "/".join(template.split("/")[-2:])
      dataExports[pathfile[:-4]] = readTemplate(rootTemplates, pathfile)

    f = open(fileExport, 'w')
    f.truncate()
    jsonExport = json.dumps(dataExports, sort_keys=True, indent=2)
    f.write("var " + export.upper() + " = " + jsonExport + ";")
    f.close()

    print "wrote %s %s to '%s' ~%s bytes" % (len(templates), export.upper(), export, len(jsonExport))
    # print jsonExport[:400]
    # print

  print "done"
  print